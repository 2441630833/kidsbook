# 执行与参数传递

只依赖终端/文件工具、Blender 自带 bpy、按需 Rokoko 和 FFmpeg。素材、对象、骨名和场景参数在每次调用时发现。下面的 `<...>` 都表示运行时提供的路径，不代表某个项目。

## 依赖与连接

从本地安装/进程/配置定位 Blender，查询插件源码与版本，不要求固定盘符、安装目录或升级。第三方官方来源：

- BlenderMCP addon.py：<https://github.com/ahujasid/blender-mcp>。
- Rokoko：<https://github.com/Rokoko/rokoko-studio-live-blender>；获取后记录版本/commit/hash，插件路径指包含 `__init__.py` 的包目录。
- FFmpeg：本机 exe 或 `imageio_ffmpeg.get_ffmpeg_exe()`；必要新依赖放项目环境，不改全局 Python。

Rokoko 登录/直播可选依赖不一定是离线重定向所需。区分可选警告和 operator 未注册的错误。

已连接 MCP：用其 execute_code 查询 `import bpy; print(bpy.app.version_string, bpy.data.filepath)`。只有官方插件 socket 时：

```text
python <skill>/scripts/mcp_call.py --port <port>
python <skill>/scripts/mcp_call.py --code <task.py> --output <response.json>
```

socket 命令格式 `{"type":"execute_code","params":{"code":"..."}}`；这是官方插件协议，不是 HTTP MCP endpoint。仅在本机回环开放，该接口可以执行代码。

如果服务未启动，可通过进程 API 加载 bootstrap，无需操作界面：

```python
import subprocess
argv = [blender_exe, '--python', bootstrap_script, '--', '--addon', addon_file, '--port', str(port)]
process = subprocess.Popen(argv)  # Windows 可加 creationflags=subprocess.CREATE_NO_WINDOW
```

正常 Blender 窗口可能出现，但 agent 不读取/操作它。不关闭用户未保存会话；优先已连接服务，或另起独立后台进程。无 UI 环境直接走 CLI，不启动官方插件后等待不存在的正常事件循环。

## 任意任务脚本

agent 在**当前任务目录**生成本次 bpy 脚本和可选 JSON，不修改 skill 来写入新素材。任务脚本获得：

- `JOB_CONFIG`：JSON 解码后的任意对象，字段由本次脚本决定，没有固定角色数量或素材组合。
- `OUTPUT_DIR`：本次 job 目录的绝对 Path。
- helper 所在目录已加入 sys.path，可 `import blender_ops`。
- 可选 `RESULT`：可 JSON 序列化的结果，宿主写入 `job_result.json`。

JSON 中路径不会自动解析。agent 应写绝对路径，或在当前任务脚本中明确相对路径基准；不要依赖 Blender 的 cwd。

例如本次任务先约定 JSON 的 `assets` 为待导入文件列表，再写：

```python
import bpy
from blender_ops import import_asset, scene_inventory

# 已有工程只检查；新建任务可在本次脚本里建立独立场景，避免混入启动默认物体。
for asset in JOB_CONFIG['assets']:
    imported = import_asset(asset['path'], asset.get('collection'))
RESULT = scene_inventory()
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / 'imported.blend'))
```

`assets` 仅为此片段的约定，不是 skill 强制 schema。后续脚本基于清单选择骨架/动作、生成映射和布置镜头。

## 后台执行

```text
python <skill>/scripts/run_blender.py <task.py> --config <inputs.json> --output <new-job-directory> --blender <blender-exe> --input <optional-working.blend>
```

不需要打开已有工程时省略 `--input`。启动 `--background --factory-startup` 独立进程后加载输入，不影响其他 Blender 会话。该路径不需要 Computer Use，也不称为 MCP 执行。

## MCP 执行

```text
python <skill>/scripts/run_blender.py <task.py> --config <inputs.json> --output <new-job-directory> --transport mcp --port <port> --input <optional-working.blend>
```

发起器向插件提交一次性 timer，立即返回，任务写状态。加载 `.blend` 后会在下一次事件循环恢复执行，以避免失效上下文。省略 `--input` 可在当前工程直接运行脚本；修改前先另存副本。

使用真实 MCP connector 时可执行等效片段，预先在本次 job 目录生成 job.json，字段为 script/output/config/input_blend：

```python
import bpy, runpy
def run_once():
    runpy.run_path(host_script_path, run_name='__main__', init_globals={'JOB_SPEC_PATH': job_spec_path})
    return None
bpy.app.timers.register(run_once, first_interval=1.0)
print('QUEUED')
```

## 状态、错误与重试

每次调用独立 job 目录。`launch.json` 有 transport/PID 或插件响应，`job_status.json` 为 queued/running/complete/error；CLI 输出在 job.log，异常 traceback 在状态中。job.json 保留参数快照。

先等上一阶段 complete，再读取其结果和工程，启动下一阶段。QUEUED/PID 仅表示提交；连接超时、进程退出或文件存在均不能单独证明成功。若 queued/running 长期不变，先查 PID、日志和 Blender，再重试，避免重复导入与覆盖。每次重试使用新目录并选择明确的输入工程。

长任务短时轮询文件，按变化反馈；不要占用一次工具调用等待整段长渲染。后台没有正常 UI loop，直接运行 render；不等待 timer。不要终止或清理不属于本任务的进程、handler 或文件。
