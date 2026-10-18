"""Inspect glTF skin/animation declarations without importing bpy or decoding textures."""
import argparse
import json
import struct
import sys
from pathlib import Path


def inspect(path):
    path = Path(path)
    if path.suffix.lower() == ".gltf":
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    else:
        with path.open("rb") as stream:
            magic, version, length = struct.unpack("<4sII", stream.read(12))
            if magic != b"glTF" or version != 2 or length != path.stat().st_size:
                raise ValueError("Not a valid glTF 2 GLB header/length")
            chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
            if chunk_type != 0x4E4F534A or chunk_length > length - 20:
                raise ValueError("GLB JSON chunk is missing or invalid")
            doc = json.loads(stream.read(chunk_length))
    skins = doc.get("skins", [])
    meshes = doc.get("meshes", [])
    influenced = sum("JOINTS_0" in p.get("attributes", {}) and "WEIGHTS_0" in p.get("attributes", {})
                     for mesh in meshes for p in mesh.get("primitives", []))
    return {"path": str(path.resolve()), "asset": doc.get("asset"), "mesh_count": len(meshes),
            "skins": [{"name": s.get("name"), "joint_count": len(s.get("joints", []))} for s in skins],
            "skinned_mesh_nodes": sum("skin" in n and "mesh" in n for n in doc.get("nodes", [])),
            "weighted_primitives": influenced,
            "animations": [{"name": a.get("name"), "channels": len(a.get("channels", []))}
                           for a in doc.get("animations", [])],
            "declares_skinning": bool(skins and influenced),
            "note": "Declarations only; validate armature modifiers, vertex groups and poses in Blender."}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = [inspect(p) for p in args.paths]
    value = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(value, encoding="utf-8")
    print(value)
