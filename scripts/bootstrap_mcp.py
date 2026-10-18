"""Start the official BlenderMCP add-on without clicking its sidebar. Run in normal Blender."""
import argparse
import importlib.util
from pathlib import Path
import sys
import bpy


def start(addon_path, port=9876):
    if bpy.app.background:
        raise RuntimeError("Official add-on needs Blender's event loop. Use run_blender.py CLI transport in background mode")
    if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
        raise RuntimeError("Server already exists; probe its port instead of starting another")
    spec = importlib.util.spec_from_file_location("blender_mcp", str(Path(addon_path).resolve()))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not hasattr(bpy.types.Scene, "blendermcp_port"):
        module.register()
    server = module.BlenderMCPServer(host="127.0.0.1", port=port)
    bpy.types.blendermcp_server = server
    server.start()
    print("BlenderMCP loopback server requested on", port, "; verify with mcp_call.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--addon", required=True)
    parser.add_argument("--port", type=int, default=9876)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    start(args.addon, args.port)
