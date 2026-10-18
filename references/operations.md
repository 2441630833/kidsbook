# Blender 操作接口

以下 helper 只封装调用，不包含模型、骨架方案或场景样式。用本次 inventory 和用户要求生成参数；特殊情况可直接写 bpy。

## 检查和导入

```text
python <skill>/scripts/inspect_glb.py <new-model.glb> --output <inventory.json>
```

这仅检查 glTF 声明，不证明权重正确。FBX 和实际 Blender 数据用任务脚本：

```python
from blender_ops import scene_inventory
RESULT = scene_inventory()
```

`import_asset(path, collection_name=None)` 支持 GLB/glTF/FBX，返回导入对象列表，保留原父子关系，不清空已有场景。可选集合名完全由任务传入。`.blend` 使用宿主 `--input` 或显式 append 所需数据。检查贴图是否 packed/路径有效，根层级、骨架修改器、非零权重、源动作 slot 与帧率；inventory 不是全部质量检查。

若需要整体变换某组导入对象，记录每个根的世界矩阵，将根统一挂到新 Empty 并保持 matrix_world，再只变换这个 Empty。不要按网格名字重排环境内部布局。包含动画/约束的根须先验证父级变换影响。

## Rokoko

1. 从实际骨名、层级及 rest head/tail 创建 source→target 映射。确认根骨、左右肢体、骨轴、A/T pose 与比例。骨名相似不足以证明对应关系。多角色分别生成映射并检查。
2. 指定正确源动作和 action slot；保存旧动作/NLA。需要校准参考姿势时只改工作副本，校准方式由本次骨架决定。不要自动套用任何角色骨数、旋转、缩放或 rest pose 修复。
3. 基本调用：

```python
from blender_ops import retarget_rokoko
RESULT = retarget_rokoko(
    source_name=JOB_CONFIG['source_armature'],
    target_name=JOB_CONFIG['target_armature'],
    mapping=JOB_CONFIG['bone_mapping'],
    addon_path=JOB_CONFIG['rokoko_path'],
    compatibility=JOB_CONFIG.get('compatibility'),
    auto_scaling=JOB_CONFIG.get('auto_scaling', True),
    use_pose=JOB_CONFIG.get('use_pose', 'REST'),
)
```

参数 source/target 是**对象名**，bone_mapping 是**骨名**映射，均来自本次检查。REST/CURRENT 要与本机插件 enum 一致。helper 保存旧目标 action 为 fake user、停用其 NLA、调用 `bpy.ops.rsl.retarget_animation()` 并检查 FINISHED 与 pose keyframes；它不自动对齐任意骨架、不保证变形质量。插件操作会改变骨架/动作，只在副本执行，成功后另存。默认不让 1.4.3 将映射写入插件全局偏好，避免不同任务互相影响；临时替换的缓存函数在 finally 恢复，只有明确需要时设置 remember_mapping=True。

处理 root motion：先识别源是 object-level 还是根骨位移；旧 Rokoko auto-scale clean 会删除对象 transform 曲线，必要时先转换/烘焙到合适根骨或选用适合的缩放流程，不能直接丢失位移。源动作共享给多个目标时保留源 action 副本，检查插件是否修改源数据。

版本兼容见 compatibility.md。`compatibility='rokoko-1.4.3-layered'` 仅用于匹配版本，不是默认必选。映射、曲线存在和成功返回不能替代逐帧检查膝盖反折、脚滑、肩扭曲和衣物穿插。

## 场景、白模与审阅

布局、比例、地面高度、相机位置/焦距、灯光、色彩管理、材质/后期均根据本次模型与需求编写脚本。背景未提供时按用户要求建立简单场景，已有环境则保持内部布局。源动作网格可通过它们实际所属集合/对象隐藏，检查 hide_render 以及父集合和辅助物体，不只凭名称前缀。

使用 `evaluated_bounds(objects, frame=...)` 获得变形后的世界 AABB。可结合 `world_to_camera_view` 逐帧检查裁切和相机前后位置；旋转/非矩形房间使用实际空间几何检查。脚底接触检查应保留跳跃或腾空，不能统一逐帧“吸地”。另检查道具遮挡和碰撞，必要时额外预览。

```python
from blender_ops import render_preview
render_preview(OUTPUT_DIR / 'preview.png', frame=JOB_CONFIG['review_frame'],
               percent=JOB_CONFIG.get('review_percent', 50), mode=JOB_CONFIG.get('preview_mode', 'clay'))
```

该函数需当前场景已有相机。clay 用 Workbench，material 使用当前引擎/材质，函数结束恢复临时设置，不依赖截图。无 OpenGL 时参照兼容文档用 Cycles CPU 临时材质覆盖。将审阅工程另存，必要时提供多帧白模预览/低分辨率动画供用户确认。

## 连续渲染和视频

agent 先根据实际授权及审阅版本设置当前 scene 的引擎、尺寸、fps/fps_base、frame_start/end 和 frame_step=1；不要从旧项目继承其参数。然后：

```python
from blender_ops import render_sequence
RESULT = render_sequence(OUTPUT_DIR / 'render', authorized=JOB_CONFIG['render_authorized'])
```

authorized 仅记录真实用户许可；要求先预览的任务不能自行设置 true。helper 按当前场景渲染，不预设镜头或帧段。另存 packed project.blend，输出 render/frames/frame_XXXX.png 和 render_progress.json；目录必须未用于其他序列。只清理自身标记 handler，异常写 error，完成校验所有期望帧。

```text
python <skill>/scripts/encode_video.py <render-directory> --ffmpeg <ffmpeg-exe> --audio <optional-authorized-audio>
```

无音轨时省略 --audio；不默认配乐。完整序列/工程哈希匹配后编码 H.264/yuv420p、AAC（如有音轨），完整解码检查帧数，保存 poster.png、video_validation.txt、delivery_manifest.json。奇数尺寸会补边到偶数，避免 yuv420p 编码失败。多视图、分段时间重映射、特殊编号/输出格式应适配 helper 或直接调用 FFmpeg，并保留等效验证。

编码很久时用后台进程和日志；Windows Start-Process 加 -WindowStyle Hidden。交付真实完成文件和验证范围，不把测试帧或旧版本当成成片。
