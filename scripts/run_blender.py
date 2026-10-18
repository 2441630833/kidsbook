"""Run any task-specific bpy script using MCP or background Blender, without UI automation."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from mcp_call import call


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Task script; receives JOB_CONFIG and OUTPUT_DIR globals")
    parser.add_argument("--output", required=True, type=Path, help="Unique job directory for status/log/result")
    parser.add_argument("--config", type=Path, help="Optional arbitrary JSON data for the task script")
    parser.add_argument("--input", type=Path, help="Optional existing blend, opened before the task script")
    parser.add_argument("--transport", choices=["cli", "mcp"], default="cli")
    parser.add_argument("--blender", help="Blender executable for CLI transport")
    parser.add_argument("--port", type=int, default=9876)
    args = parser.parse_args()
    script = args.script.resolve()
    if not script.is_file():
        parser.error("Script does not exist: " + str(script))
    if args.input and not args.input.is_file():
        parser.error("Input blend does not exist")
    if args.transport == "cli" and not args.blender:
        parser.error("--blender is required for CLI transport")
    config = json.loads(args.config.read_text(encoding="utf-8-sig")) if args.config else {}
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    status = output / "job_status.json"
    if status.exists() or (output / "job.json").exists():
        parser.error("Job directory already used. Inspect its result/process and choose a new directory for another call")
    spec = {"script": str(script), "output": str(output), "config": config,
            "input_blend": str(args.input.resolve()) if args.input else None,
            "transport": args.transport}
    spec_path = output / "job.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    status.write_text(json.dumps({"state": "queued", "queued_at": time.time()}), encoding="utf-8")
    host = Path(__file__).with_name("job_host.py")
    if args.transport == "cli":
        command = [args.blender, "--background", "--factory-startup", "--python-exit-code", "1",
                   "--python", str(host), "--", "--job", str(spec_path)]
        log = output / "job.log"
        try:
            with log.open("w", encoding="utf-8") as stream:
                process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        except OSError as error:
            status.write_text(json.dumps({"state": "error", "error": str(error)}), encoding="utf-8")
            raise
        result = {"transport": "cli", "pid": process.pid, "log": str(log)}
    else:
        code = ("import bpy, runpy\n"
                "if bpy.app.background: raise RuntimeError('Use CLI transport in background Blender')\n"
                "def _animation_skill_task():\n"
                f"    runpy.run_path({str(host)!r}, run_name='__main__', init_globals={{'JOB_SPEC_PATH': {str(spec_path)!r}}})\n"
                "    return None\n"
                "bpy.app.timers.register(_animation_skill_task, first_interval=1.0)\n"
                "print('QUEUED: inspect job_status.json for completion')\n")
        # A timeout can occur after execution was queued: leave status queued, inspect before retrying.
        result = call({"type": "execute_code", "params": {"code": code}}, port=args.port, timeout=15)
    result["job_directory"] = str(output)
    (output / "launch.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
