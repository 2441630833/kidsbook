"""Optional bpy helpers; discover assets/rigs/layout at use time, never from a previous project."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import traceback
import bpy
from mathutils import Vector
from job_host import write_json
from skill_rokoko_compat import curves


def import_asset(path, collection_name=None):
    """Import GLB/glTF/FBX without clearing the scene or altering the imported hierarchy."""
    path = Path(path).resolve()
    before = set(bpy.data.objects)
    if path.suffix.lower() in {".glb", ".gltf"}:
        result = bpy.ops.import_scene.gltf(filepath=str(path))
    elif path.suffix.lower() == ".fbx":
        result = bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError("Use GLB/glTF/FBX, or append selected datablocks from a blend explicitly")
    if result != {"FINISHED"}:
        raise RuntimeError("Import failed: " + str(result))
    objects = list(set(bpy.data.objects) - before)
    if collection_name:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)
        for obj in objects:
            for old in list(obj.users_collection):
                old.objects.unlink(obj)
            coll.objects.link(obj)
    return objects


def skinned_meshes(armature):
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"
            and any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)]


def scene_inventory():
    scene = bpy.context.scene
    objects = []
    for obj in scene.objects:
        item = {"name": obj.name, "type": obj.type, "parent": obj.parent.name if obj.parent else None,
                "collections": [c.name for c in obj.users_collection], "hide_render": obj.hide_render}
        if obj.type == "MESH":
            item.update(vertices=len(obj.data.vertices), vertex_groups=[g.name for g in obj.vertex_groups],
                        weighted_vertices=sum(any(g.weight > 0 for g in v.groups) for v in obj.data.vertices),
                        armatures=[m.object.name for m in obj.modifiers if m.type == "ARMATURE" and m.object],
                        materials=[m.name for m in obj.data.materials if m])
        if obj.type == "ARMATURE":
            item["bones"] = [{"name": b.name, "parent": b.parent.name if b.parent else None,
                              "head": list(b.head_local), "tail": list(b.tail_local)} for b in obj.data.bones]
            item["skinned_meshes"] = [m.name for m in skinned_meshes(obj)]
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            slot = getattr(obj.animation_data, "action_slot", None)
            item["action"] = {"name": action.name, "range": list(action.frame_range),
                              "slot": getattr(slot, "identifier", None), "curves": len(curves(action, obj))}
        objects.append(item)
    return {"blender": bpy.app.version_string, "blend": bpy.data.filepath,
            "scene": scene.name, "camera": scene.camera.name if scene.camera else None,
            "fps": scene.render.fps / scene.render.fps_base,
            "frames": [scene.frame_start, scene.frame_end], "objects": objects}


def evaluated_bounds(objects, frame=None):
    """World AABBs, not a furniture collision/visibility detector."""
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result = {}
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
        result[obj.name] = [min(p[i] for p in points) for i in range(3)] + [max(p[i] for p in points) for i in range(3)]
    return result


def retarget_rokoko(source_name, target_name, mapping, addon_path, compatibility=None,
                    auto_scaling=True, use_pose="REST", remember_mapping=False):
    """Use discovered object/bone names. Reference-pose alignment is rig-specific and done beforehand."""
    scene = bpy.context.scene
    source, target = scene.objects[source_name], scene.objects[target_name]
    if source == target or source.type != "ARMATURE" or target.type != "ARMATURE":
        raise ValueError("Choose distinct source/target armatures from the current inventory")
    if not source.animation_data or not source.animation_data.action:
        raise ValueError("Assign the requested source action and actual action slot first")
    meshes = skinned_meshes(target)
    if not meshes or not any(any(g.weight > 0 for v in m.data.vertices for g in v.groups) for m in meshes):
        raise ValueError("Target must have armature modifiers and weighted vertices")
    if not mapping or len(set(mapping.values())) != len(mapping):
        raise ValueError("Mapping must be nonempty, with unique target bones")
    missing = [(a, b) for a, b in mapping.items() if a not in source.pose.bones or b not in target.pose.bones]
    if missing:
        raise ValueError("Mapped bones not found: " + str(missing))
    plugin = Path(addon_path).resolve()
    sys.path.insert(0, str(plugin.parent))
    addon = importlib.import_module(plugin.name)
    if not hasattr(bpy.types.Scene, "rsl_retargeting_armature_source"):
        addon.register()
    if compatibility == "rokoko-1.4.3-layered":
        from skill_rokoko_compat import apply
        apply(plugin.name)
    elif compatibility is not None:
        raise ValueError("Unknown compatibility mode; inspect the installed plugin before adapting it")
    if target.animation_data:
        if target.animation_data.action:
            target.animation_data.action.use_fake_user = True
            target.animation_data.action = None
        for track in target.animation_data.nla_tracks:
            track.mute = True
    source_action = source.animation_data.action.name
    scene.rsl_retargeting_armature_source = source
    scene.rsl_retargeting_armature_target = target
    scene.rsl_retargeting_auto_scaling = auto_scaling
    scene.rsl_retargeting_use_pose = use_pose
    scene.rsl_retargeting_bone_list.clear()
    for a, b in mapping.items():
        item = scene.rsl_retargeting_bone_list.add()
        item.bone_name_source, item.bone_name_target = a, b
    # Mapping is explicit for this invocation. Old Rokoko's preference cache can fail for
    # manually mapped/unanimated source bones; do not persist cross-task mappings by default.
    cache = None
    original_save = None
    if not remember_mapping and tuple(addon.bl_info.get("version", ())) == (1, 4, 3):
        cache = importlib.import_module(plugin.name + ".core.custom_schemes_manager")
        original_save = cache.save_retargeting_to_list
        cache.save_retargeting_to_list = lambda: None
    try:
        result = bpy.ops.rsl.retarget_animation()
    finally:
        if cache is not None:
            cache.save_retargeting_to_list = original_save
    if result != {"FINISHED"} or not target.animation_data or not target.animation_data.action:
        raise RuntimeError("Rokoko failed: " + str(result))
    channels = curves(target.animation_data.action, target)
    if not any(c.data_path.startswith("pose.bones[") and len(c.keyframe_points) > 1 for c in channels):
        raise RuntimeError("Rokoko produced no keyed pose channels")
    bpy.context.view_layer.update()
    return {"operator": "rsl.retarget_animation", "rokoko_version": list(addon.bl_info["version"]),
            "source_action": source_action, "target_action": target.animation_data.action.name,
            "range": list(target.animation_data.action.frame_range), "channels": len(channels)}


def render_preview(path, frame=None, percent=50, mode="material"):
    """Transient camera render; preserves project engine, materials and render settings."""
    scene = bpy.context.scene
    if not scene.camera:
        raise ValueError("Create and aim a camera from the current scene first")
    if mode not in {"material", "clay"}:
        raise ValueError("Preview mode must be material or clay")
    saved = (scene.render.engine, scene.render.filepath, scene.render.resolution_percentage,
             scene.render.use_compositing, scene.render.image_settings.file_format, scene.frame_current,
             scene.display.shading.light, scene.display.shading.color_type,
             tuple(scene.display.shading.single_color))
    try:
        if frame is not None:
            scene.frame_set(frame)
        scene.render.filepath = str(Path(path).resolve())
        scene.render.resolution_percentage = percent
        scene.render.image_settings.file_format = "PNG"
        if mode == "clay":
            scene.render.engine = "BLENDER_WORKBENCH"
            scene.render.use_compositing = False
            scene.display.shading.light, scene.display.shading.color_type = "STUDIO", "SINGLE"
            scene.display.shading.single_color = (.72, .72, .72)
        if bpy.ops.render.render(write_still=True) != {"FINISHED"}:
            raise RuntimeError("Preview render cancelled")
    finally:
        (scene.render.engine, scene.render.filepath, scene.render.resolution_percentage,
         scene.render.use_compositing, scene.render.image_settings.file_format, frame,
         scene.display.shading.light, scene.display.shading.color_type,
         scene.display.shading.single_color) = saved
        scene.frame_set(frame)


def render_sequence(output, *, authorized=False):
    """Render the current, reviewed scene/settings. No preset camera, model, frame range or engine."""
    if not authorized:
        raise ValueError("Full render needs actual user authorization; the flag only records it")
    scene = bpy.context.scene
    if not scene.camera or scene.frame_end < scene.frame_start or scene.frame_step != 1:
        raise ValueError("Need a camera, valid frame range, and frame_step=1")
    if scene.render.use_multiview:
        raise ValueError("Adapt sequence naming/encoding for multiview before rendering")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    frames = output / "frames"
    frames.mkdir(exist_ok=True)
    if list(frames.iterdir()) or (output / "render_progress.json").exists():
        raise ValueError("Render directory already used; use a new version directory")
    scene.use_preview_range = False
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.use_file_extension = True
    scene.render.filepath = str(frames / "frame_")
    scene.frame_set(scene.frame_start)
    bpy.ops.file.pack_all()
    project = output / "project.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(project))
    blend_hash = hashlib.sha256(project.read_bytes()).hexdigest()
    base = {"start": scene.frame_start, "end": scene.frame_end,
            "fps": scene.render.fps / scene.render.fps_base,
            "total": scene.frame_end - scene.frame_start + 1, "blend_sha256": blend_hash}
    base["render_signature"] = hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest()
    status = output / "render_progress.json"
    started = time.time()

    def progress(current, *_args):
        write_json(status, dict(base, state="rendering", frame=current.frame_current, elapsed=time.time() - started))

    progress._blender_animation_skill = True
    for old in list(bpy.app.handlers.render_write):
        if getattr(old, "_blender_animation_skill", False):
            bpy.app.handlers.render_write.remove(old)
    bpy.app.handlers.render_write.append(progress)
    try:
        write_json(status, dict(base, state="rendering", frame=None))
        if bpy.ops.render.render(animation=True) != {"FINISHED"}:
            raise RuntimeError("Render cancelled")
        expected = {f"frame_{i:04d}.png" for i in range(base["start"], base["end"] + 1)}
        actual = {p.name for p in frames.glob("*.png")}
        if actual != expected or any((frames / p).stat().st_size == 0 for p in expected):
            raise RuntimeError("Rendered frame sequence is incomplete")
        write_json(status, dict(base, state="complete", elapsed=time.time() - started))
    except BaseException:
        write_json(status, dict(base, state="error", traceback=traceback.format_exc()))
        raise
    finally:
        if progress in bpy.app.handlers.render_write:
            bpy.app.handlers.render_write.remove(progress)
    return base
