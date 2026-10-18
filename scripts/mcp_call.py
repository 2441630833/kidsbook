"""Official BlenderMCP add-on's local JSON socket; no browser or UI automation."""
import argparse
import ipaddress
import json
import socket
import sys
import time
from pathlib import Path


def call(command, host="127.0.0.1", port=9876, timeout=30):
    if host != "localhost" and not ipaddress.ip_address(host).is_loopback:
        raise ValueError("The unauthenticated Blender add-on must stay on loopback")
    deadline = time.monotonic() + timeout
    with socket.create_connection((host, port), timeout=min(timeout, 10)) as sock:
        sock.sendall(json.dumps(command, ensure_ascii=False).encode("utf-8"))
        data = bytearray()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("No complete response; inspect Blender before retrying a mutation")
            sock.settimeout(remaining)
            part = sock.recv(65536)
            if not part:
                raise ConnectionError("Blender closed the socket before returning complete JSON")
            data.extend(part)
            if len(data) > 32 * 1024 * 1024:
                raise ValueError("Response exceeds 32 MiB")
            try:
                result = json.loads(data)
                break
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
    # execute_code has an outer transport result and an inner operation result.
    def check(value):
        if isinstance(value, dict):
            if value.get("status") == "error" or value.get("executed") is False:
                raise RuntimeError(json.dumps(value, ensure_ascii=False))
            for key in ("result", "data"):
                if key in value:
                    check(value[key])
        elif isinstance(value, str):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                return
            check(decoded)
    check(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--code", type=Path, help="UTF-8 Python file executed inside Blender")
    group.add_argument("--request", type=Path, help="Complete command JSON for another add-on command")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9876)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    command = {"type": "execute_code", "params": {"code": "import bpy; print(bpy.app.version_string)"}}
    if args.code:
        command["params"]["code"] = args.code.read_text(encoding="utf-8-sig")
    if args.request:
        command = json.loads(args.request.read_text(encoding="utf-8-sig"))
    result = call(command, args.host, args.port, args.timeout)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
