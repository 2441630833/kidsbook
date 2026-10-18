"""Blender-side generic task host; no asset names, scene layout, frame range or rig assumptions."""
import argparse
import json
from pathlib import Path
import runpy
import sys
import time
import traceback
import bpy


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def execute(spec_path, load_input=True):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8-sig"))
    output = Path(spec["output"])
    status = output / "job_status.json"
    started = time.time()
    write_json(status, {"state": "running", "script": spec["script"], "started": started})
    try:
        if load_input and spec.get("input_blend"):
            bpy.ops.wm.open_mainfile(filepath=spec["input_blend"])
            if not bpy.app.background:
                # Loading a blend invalidates this timer context. Resume on a fresh UI tick.
                bpy.app.timers.register(lambda: execute(spec_path, load_input=False), first_interval=.25)
                return
        scripts = str(Path(__file__).resolve().parent)
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        globals_in = {"JOB_CONFIG": spec.get("config", {}), "OUTPUT_DIR": output}

        def run():
            return runpy.run_path(spec["script"], run_name="__main__", init_globals=globals_in)

        window = bpy.context.window
        if window is None and bpy.context.window_manager.windows:
            window = bpy.context.window_manager.windows[0]
        if window is not None:
            with bpy.context.temp_override(window=window):
                result = run()
        else:
            result = run()
        if "RESULT" in result:
            write_json(output / "job_result.json", result["RESULT"])
        write_json(status, {"state": "complete", "elapsed": time.time() - started})
    except BaseException:
        write_json(status, {"state": "error", "traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    if "JOB_SPEC_PATH" in globals():
        execute(JOB_SPEC_PATH)
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--job", required=True)
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
        execute(args.job)
