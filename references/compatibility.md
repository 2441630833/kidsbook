# 版本与故障

按运行时探测到的 Blender 和插件版本选择兼容方案。下列经验来自 Blender 5.2.2 LTS / Rokoko 1.4.3 的 API 差异，不要求新任务使用这些版本。

| 症状 | 处理 |
| --- | --- |
| Action.fcurves 不存在 | 用所属对象的 animation_data.action_slot 遍历 layer/strip/channelbag；不要任取第一个 slot。附带 shim 已实现。 |
| Bone.select 不存在 | 5.2 使用 PoseBone.select，EditBone.select 仍可用。shim 仅替换目标骨选择，不全局替换。 |
| Rokoko 分段 bake/merge 依赖旧 API | 1.4.3 shim 一次 nla.bake 全帧段，visual_keying/POSE，删除非根位移和缩放；仍实际调用 Rokoko operator，核对 FINISHED 和多帧 pose 曲线。 |
| 1.4.3 保存手工映射时报 KeyError | 偏好缓存可能只包含已动画/已识别骨。显式映射调用无需写全局偏好；helper 默认在本次 operator 内停用缓存写入并 finally 恢复，仍使用本次传入的映射。 |
| Scene.node_tree 不存在 | 新版用 compositing_node_group + CompositorNodeTree/interface Image 输出，旧版 scene.node_tree。 |
| Glare glare_type/quality 不存在 | 新版 inputs Type=Fog Glow、Quality=High、Threshold/Strength/Size；旧版按属性 feature detection。 |
| FFMPEG file_format 枚举报错 | 统一 PNG → 外部 FFmpeg H.264/AAC，检查完整解码帧数。 |
| context.screen 为 None | 后台不要操作 screen/area/viewport；用 Workbench 白模渲染。 |
| MCP timer 中 open_mainfile 后 Context.object 缺失 | 加载文件使旧回调上下文失效；返回事件循环，再注册一次性 timer 执行后续任务，脚本已处理。 |
| GPUOffscreen 截屏失败 | 不把截图作为交付前提。Workbench 也需要图形后端；没有 EGL/OpenGL 时用 Cycles CPU + 临时灰材质覆盖、禁后期，try/finally 恢复，再渲染单帧。 |
| Windows GBK UnicodeEncodeError | 外部 stdout 配 UTF-8，JSON/脚本用 UTF-8，subprocess 参数列表传递，不把执行代码拼进 shell。 |
| MCP 长时间无响应 | timer 排队马上返回或后台 CLI；socket timeout 不代表可以盲目重试。 |
| 旧 progress 文件重新更新 | 遗留 render_write handler；只清自己标记的 handler，并在 finally 清理，不能清空用户 handler。 |
| 裙摆/膝盖塌陷 | 区分无 skin、错误权重、参考姿势/尺度/骨轴不匹配。临时 auto-rig 不等于可靠角色；按用户最新选择换模型或移除。 |
| 环境渲染与参考不同 | 先恢复原几何布局和贴图，再调灯光/后期；不要用遮挡物或强环境光掩盖结构错误。 |

兼容补丁从原文件 AST 提取目标函数并核对源码片段，仅在当前会话替换函数。版本或结构不符则报错，需阅读当前插件适配；不盲改全局安装，不把完整第三方插件打进技能包。
