"""Skill-local compatibility for Rokoko 1.4.3 on layered-action Blender versions."""
import ast
import importlib
from pathlib import Path
import re
import textwrap
import bpy


def curve_collections(action, obj):
    if hasattr(action, "fcurves"):
        return [action.fcurves]
    if not obj.animation_data or obj.animation_data.action != action:
        raise ValueError("Resolve layered channels using the actual owning object")
    slot = obj.animation_data.action_slot
    if slot is None:
        raise ValueError("Object has no assigned action slot")
    groups = []
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbag"):
                bag = strip.channelbag(slot)
                if bag is not None:
                    groups.append(bag.fcurves)
    return groups


def curves(action, obj):
    return [c for group in curve_collections(action, obj) for c in group]


def original_source(module, name, parent=None):
    code = Path(module.__file__).read_text(encoding="utf-8-sig")
    nodes = ast.parse(code).body
    if parent:
        nodes = next(n for n in nodes if isinstance(n, ast.ClassDef) and n.name == parent).body
    node = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    return textwrap.dedent("\n".join(code.splitlines()[node.lineno - 1:node.end_lineno]))


def apply(package):
    addon = importlib.import_module(package)
    version = tuple(addon.bl_info.get("version", ()))
    if version != (1, 4, 3):
        raise RuntimeError(f"Compatibility shim targets Rokoko 1.4.3, found {version}; inspect its API first")
    mod = importlib.import_module(package + ".operators.retargeting")
    det = importlib.import_module(package + ".core.detection_manager")
    if mod.__dict__.get("_animation_skill_patched"):
        return

    def clean(self, arm):
        for group in curve_collections(arm.animation_data.action, arm):
            for curve in list(group):
                if curve.data_path in {"location", "rotation_euler", "rotation_quaternion", "scale"}:
                    group.remove(curve)

    def interval(self, arm):
        return tuple(arm.animation_data.action.frame_range)

    def bake(self, source, target, roots):
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.mode_set(mode="POSE")
        start, end = map(int, source.animation_data.action.frame_range)
        result = bpy.ops.nla.bake(frame_start=start, frame_end=end, step=1,
                                  visual_keying=True, only_selected=True,
                                  use_current_action=False, bake_types={"POSE"})
        if result != {"FINISHED"}:
            raise RuntimeError("Pose bake failed: " + str(result))
        bpy.ops.object.mode_set(mode="OBJECT")
        action = target.animation_data.action
        for group in curve_collections(action, target):
            for curve in list(group):
                match = re.match(r'pose\.bones\["(.+)"\]\.location$', curve.data_path)
                if curve.data_path.endswith("scale") or (match and match[1] not in roots):
                    group.remove(curve)
        action.use_fake_user = True

    detect = original_source(det, "detect_retarget_bones")
    old = "armature_source.animation_data.action.fcurves"
    if old not in detect:
        raise RuntimeError("Unexpected detector source; do not apply a blind text patch")
    execute = original_source(mod, "execute", "RetargetAnimation")
    old_select = "armature_target.data.bones.get(item.bone_name_target).select"
    if old_select not in execute:
        raise RuntimeError("Unexpected retarget operator source; inspect the installed add-on")
    det.__dict__["action_curves"] = curves
    exec(detect.replace(old, "action_curves(armature_source.animation_data.action, armature_source)"), det.__dict__)
    if not hasattr(bpy.types.Bone, "select"):
        execute = execute.replace(old_select, "armature_target.pose.bones.get(item.bone_name_target).select")
    exec(execute, mod.__dict__)
    mod.RetargetAnimation.execute = mod.__dict__["execute"]
    mod.RetargetAnimation.clean_animation = clean
    mod.RetargetAnimation.read_anim_start_end = interval
    mod.RetargetAnimation.bake_animation = bake
    mod.__dict__["_animation_skill_patched"] = True
