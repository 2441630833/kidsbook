"""
KidsBook 3D Asset Generator - High-Fidelity Character & Scene Pipeline
Builds vibrant, tactile 3D storybook dioramas for Beatrix Potter's The Tale of Peter Rabbit (1902 - Public Domain).
Integrates real stylized 3D assets (Bed, Table, Fence, Carrots, Berry Bush, Wildflowers, Crow)
with correctly oriented plush Peter Rabbit character, rich Beatrix Potter palette, and warm lighting in Blender 5.2.2 LTS.
"""
import bpy
import math
import os
import json
from mathutils import Vector, Euler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "assets", "models")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "assets", "renders")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

PLUSH_BUNNY_SRC = os.path.join(ASSETS_DIR, "plush_bunny.glb")
CROW_SRC = os.path.join(ASSETS_DIR, "crow_animated.glb")
BED_SRC = os.path.join(ASSETS_DIR, "Bed_Single.glb")
TABLE_SRC = os.path.join(ASSETS_DIR, "Table_RoundSmall.glb")
FENCE_SRC = os.path.join(ASSETS_DIR, "Fence.glb")
CARROT_SRC = os.path.join(ASSETS_DIR, "Carrot_Crop.glb")
BUSH_SRC = os.path.join(ASSETS_DIR, "BushBerries_1.glb")
FLOWERS_SRC = os.path.join(ASSETS_DIR, "Flowers.glb")
ROCK_SRC = os.path.join(ASSETS_DIR, "Rock_Moss_1.glb")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

def reset_scene():
    """Clear scene for clean procedural generation."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if "Scene" not in bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.data.scenes[0]
    bpy.context.window.scene = scene
    # Ambient fill for rendering
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs['Color'].default_value = (0.92, 0.90, 0.86, 1.0)
            bg.inputs['Strength'].default_value = 0.6
    return scene

def create_mat(name, color, roughness=0.6, metallic=0.0, emission=None, emission_strength=1.0):
    """Create a Principled BSDF material compatible with Blender 4.x / 5.x."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission[:3], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def import_glb_part(filepath, name_prefix="Part"):
    """Imports a GLB model and returns list of its mesh objects."""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found!")
        return []
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = [o for o in bpy.data.objects if o not in before]
    for idx, o in enumerate(imported):
        if o.type == 'MESH':
            o.name = f"{name_prefix}_{idx}"
    return imported

def load_and_style_peter(location=(0,0,0), scale=(0.35, 0.35, 0.35), rotation=(0,0,0), has_coat=True, pose="standing", name_prefix="Peter"):
    """
    Imports the plush bunny asset, corrects its orientation to upright (-90 deg X),
    customizes it with Peter Rabbit's warm palette, vibrant blue coat, and golden buttons.
    """
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=PLUSH_BUNNY_SRC)
    imported = [o for o in bpy.data.objects if o not in before_objs and o.type == 'MESH']
    
    # Rich Beatrix Potter Palette
    mat_fur = create_mat(f"{name_prefix}_Fur", (0.72, 0.44, 0.22), roughness=0.82)
    mat_cream = create_mat(f"{name_prefix}_Cream", (0.96, 0.92, 0.85), roughness=0.75)
    mat_pink = create_mat(f"{name_prefix}_Pink", (0.95, 0.58, 0.62), roughness=0.55)
    mat_eyes = create_mat(f"{name_prefix}_Eyes", (0.04, 0.03, 0.03), roughness=0.08, metallic=0.4)
    mat_nose = create_mat(f"{name_prefix}_Nose", (0.92, 0.48, 0.48), roughness=0.5)
    mat_coat = create_mat(f"{name_prefix}_Coat", (0.10, 0.35, 0.85), roughness=0.45)
    mat_gold = create_mat(f"{name_prefix}_Gold", (0.95, 0.78, 0.18), roughness=0.25, metallic=0.88)
    
    # Map imported parts
    for obj in imported:
        n = obj.name.lower()
        obj.data.materials.clear()
        if 'muzzle' in n:
            obj.data.materials.append(mat_cream)
        elif 'belly' in n:
            obj.data.materials.append(mat_coat if has_coat else mat_cream)
        elif 'inner' in n:
            obj.data.materials.append(mat_pink)
        elif 'nose' in n:
            obj.data.materials.append(mat_nose)
        elif 'eye' in n:
            obj.data.materials.append(mat_eyes)
        elif 'bow' in n:
            obj.data.materials.append(mat_coat if has_coat else mat_fur)
        elif 'body' in n and has_coat:
            obj.data.materials.append(mat_coat)
        else:
            obj.data.materials.append(mat_fur)
            
    # Parent to an internal orientation empty to make upright
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    bunny_orient = bpy.context.active_object
    bunny_orient.name = f"{name_prefix}_Orient"
    bunny_orient.rotation_euler = (math.radians(-90), 0, 0)
    
    for obj in imported:
        obj.parent = bunny_orient

    # 3 golden brass buttons down the chest in FRONT of the jacket
    if has_coat:
        for bz in [1.65, 1.35, 1.05]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, -0.95, bz))
            btn = bpy.context.active_object
            btn.name = f"{name_prefix}_Button"
            btn.data.materials.append(mat_gold)
            btn.parent = bunny_orient
            btn.matrix_parent_inverse = bunny_orient.matrix_world.inverted()
            
    # Top-level control root
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"{name_prefix}_Root"
    bunny_orient.parent = root
    
    # Apply transform
    root.location = location
    root.scale = scale
    root.rotation_euler = Euler(rotation, 'XYZ')
    
    # Poses
    if pose == "eating":
        bunny_orient.rotation_euler.x = math.radians(-75)
    elif pose == "sleeping":
        bunny_orient.rotation_euler = Euler((math.radians(-10), math.radians(80), 0), 'XYZ')
        
    return root

# =========================================================================
# Chapter Dioramas
# =========================================================================

def build_scene1_burrow():
    """Chapter 1: The Cozy Burrow under the Giant Fir Tree."""
    reset_scene()
    
    mat_earth = create_mat("M_Earth", (0.28, 0.16, 0.08), roughness=0.88)
    mat_bark = create_mat("M_Bark", (0.22, 0.12, 0.06), roughness=0.92)
    mat_teapot = create_mat("M_Teapot", (0.92, 0.94, 0.96), roughness=0.15)
    mat_lantern_brass = create_mat("M_LanternBrass", (0.90, 0.75, 0.25), roughness=0.3, metallic=0.85)
    mat_lantern_light = create_mat("M_LanternGlow", (1.0, 0.9, 0.5), roughness=0.1, emission=(1.0, 0.85, 0.4), emission_strength=5.0)

    # 1. Burrow Floor Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    floor = bpy.context.active_object
    floor.name = "Burrow_Floor"
    floor.data.materials.append(mat_earth)
    
    # 2. Cozy Bed (Real Model)
    bed_objs = import_glb_part(BED_SRC, "Bed")
    if bed_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-1.35, 0.4, 0.0))
        bed_root = bpy.context.active_object
        bed_root.name = "Bed_Root"
        bed_root.scale = (0.80, 0.80, 0.80)
        bed_root.rotation_euler = (0, 0, math.radians(22))
        for o in bed_objs:
            if o != bed_root: o.parent = bed_root
            
    # 3. Round Tea Table (Real Model)
    tbl_objs = import_glb_part(TABLE_SRC, "Table")
    if tbl_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.35, 0.3, 0.0))
        tbl_root = bpy.context.active_object
        tbl_root.name = "Table_Root"
        tbl_root.scale = (0.95, 0.95, 0.95)
        for o in tbl_objs:
            if o != tbl_root: o.parent = tbl_root
            
    # 4. Ceramic Teapot & Teacup on Table
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(1.25, 0.3, 0.75))
    pot = bpy.context.active_object
    pot.name = "Teapot_Body"
    pot.data.materials.append(mat_teapot)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045, depth=0.07, location=(1.45, 0.4, 0.72))
    cup = bpy.context.active_object
    cup.name = "Teacup"
    cup.data.materials.append(mat_teapot)

    # 5. Tree Trunk & Root Arch
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.95, depth=3.2, location=(-1.3, 1.2, 1.4))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Trunk"
    trunk.rotation_euler = (math.radians(10), math.radians(-14), 0)
    trunk.data.materials.append(mat_bark)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.28, major_segments=24, minor_segments=12, location=(0, 0.7, 1.0))
    arch = bpy.context.active_object
    arch.name = "Root_Arch"
    arch.scale = (1.1, 0.65, 1.0)
    arch.rotation_euler = (math.radians(65), 0, math.radians(20))
    arch.data.materials.append(mat_bark)

    # 6. Hanging Lantern
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.22, location=(0.0, 0.2, 1.5))
    lantern = bpy.context.active_object
    lantern.name = "Lantern_Glass"
    lantern.data.materials.append(mat_lantern_light)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.12, depth=0.04, location=(0.0, 0.2, 1.63))
    lantern_cap = bpy.context.active_object
    lantern_cap.name = "Lantern_Cap"
    lantern_cap.data.materials.append(mat_lantern_brass)
    
    # 7. Peter Rabbit (Standing attentive in center of burrow)
    load_and_style_peter(
        location=(0.0, -0.2, 0.0),
        scale=(0.30, 0.30, 0.30),
        rotation=(0, 0, math.radians(10)),
        has_coat=True,
        pose="standing",
        name_prefix="Peter_Burrow"
    )
    
    # Lighting & Camera
    bpy.ops.object.light_add(type='SUN', location=(3.5, -4.5, 5.0))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.data.color = (1.0, 0.95, 0.88)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    
    bpy.ops.object.light_add(type='POINT', location=(0.0, 0.2, 1.5))
    pt = bpy.context.active_object
    pt.data.energy = 25.0
    pt.data.color = (1.0, 0.85, 0.5)
    
    bpy.ops.object.camera_add(location=(0.0, -4.8, 2.3))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(68), 0, 0)
    cam.data.lens = 38
    bpy.context.scene.camera = cam

def build_scene2_garden():
    """Chapter 2: Mr. McGregor's Secret Garden with Carrots and Watering Can."""
    reset_scene()
    
    mat_grass = create_mat("M_Grass", (0.25, 0.55, 0.16), roughness=0.85)
    mat_soil = create_mat("M_Soil", (0.32, 0.18, 0.09), roughness=0.92)
    mat_cabbage = create_mat("M_Cabbage", (0.42, 0.72, 0.25), roughness=0.65)
    mat_can = create_mat("M_WaterCan", (0.85, 0.15, 0.12), roughness=0.35)
    mat_metal = create_mat("M_Zinc", (0.75, 0.80, 0.82), roughness=0.3, metallic=0.85)
    mat_carrot = create_mat("M_CarrotOrange", (0.96, 0.45, 0.05), roughness=0.45)
    
    # 1. Garden Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    ground = bpy.context.active_object
    ground.name = "Garden_Ground"
    ground.data.materials.append(mat_grass)
    
    # 2. Raised Soil Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, 0.1, 0.1))
    soil_bed = bpy.context.active_object
    soil_bed.name = "Soil_Bed"
    soil_bed.scale = (1.5, 2.0, 0.2)
    soil_bed.data.materials.append(mat_soil)
    
    # 3. Wooden Picket Fence (Real Models)
    for fx, frot in [(-1.2, -10), (0.0, 0), (1.2, 10)]:
        f_objs = import_glb_part(FENCE_SRC, "Fence")
        if f_objs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(fx, 1.4, 0.0))
            f_root = bpy.context.active_object
            f_root.scale = (1.3, 1.3, 1.3)
            f_root.rotation_euler = (0, 0, math.radians(frot))
            for o in f_objs:
                if o != f_root: o.parent = f_root
                
    # 4. Real Carrots in Rows (Emerging vibrantly above soil)
    carrot_coords = [
        (-1.0, -0.4), (-0.6, -0.4), (-0.2, -0.4),
        (-1.0, 0.1),  (-0.6, 0.1),  (-0.2, 0.1),
        (-1.0, 0.6),  (-0.6, 0.6),  (-0.2, 0.6)
    ]
    for i, (cx, cy) in enumerate(carrot_coords):
        c_objs = import_glb_part(CARROT_SRC, f"Carrot_{i}")
        if c_objs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(cx, cy, 0.28))
            c_root = bpy.context.active_object
            c_root.name = f"Carrot_{i}"
            c_root.scale = (0.85, 0.85, 0.85)
            for o in c_objs:
                if o != c_root: o.parent = c_root
                
    # Extra freshly pulled carrot lying beside Peter
    pulled_c = import_glb_part(CARROT_SRC, "Pulled_Carrot")
    if pulled_c:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.05, -0.35, 0.22))
        pc_root = bpy.context.active_object
        pc_root.scale = (0.85, 0.85, 0.85)
        pc_root.rotation_euler = (math.radians(80), math.radians(15), math.radians(45))
        for o in pulled_c:
            if o != pc_root: o.parent = pc_root
                
    # 5. Cabbages
    for i, (cbx, cby) in enumerate([(0.7, -0.5), (0.8, 0.1), (0.7, 0.7)]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.22, location=(cbx, cby, 0.18))
        cab = bpy.context.active_object
        cab.name = f"Cabbage_{i}"
        cab.scale = (1.1, 1.1, 0.8)
        cab.data.materials.append(mat_cabbage)
        
    # 6. Classic Red Watering Can
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.22, depth=0.36, location=(1.25, -0.4, 0.18))
    can_body = bpy.context.active_object
    can_body.name = "WaterCan_Body"
    can_body.data.materials.append(mat_can)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045, depth=0.38, location=(1.10, -0.6, 0.28))
    spout = bpy.context.active_object
    spout.name = "WaterCan_Spout"
    spout.rotation_euler = (math.radians(45), 0, math.radians(-30))
    spout.data.materials.append(mat_metal)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.025, location=(1.40, -0.25, 0.25))
    handle = bpy.context.active_object
    handle.name = "WaterCan_Handle"
    handle.rotation_euler = (math.radians(90), math.radians(25), 0)
    handle.data.materials.append(mat_can)
    
    # 7. Peter Rabbit eating carrot (Standing on top of soil bed at z=0.20)
    peter = load_and_style_peter(
        location=(-0.35, -0.45, 0.20),
        scale=(0.28, 0.28, 0.28),
        rotation=(0, 0, math.radians(-25)),
        has_coat=True,
        pose="eating",
        name_prefix="Peter_Garden"
    )
    
    # Carrot in paws
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.045, depth=0.22, location=(-0.35, -0.58, 0.55))
    held_carrot = bpy.context.active_object
    held_carrot.name = "Held_Carrot"
    held_carrot.rotation_euler = (math.radians(65), math.radians(20), 0)
    held_carrot.data.materials.append(mat_carrot)
    held_carrot.parent = peter
    
    # Lighting & Camera
    bpy.ops.object.light_add(type='SUN', location=(3.5, -4.0, 5.5))
    sun = bpy.context.active_object
    sun.data.energy = 2.2
    sun.data.color = (1.0, 0.98, 0.90)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-40))
    
    bpy.ops.object.camera_add(location=(0.0, -4.6, 2.4))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(67), 0, 0)
    cam.data.lens = 38
    bpy.context.scene.camera = cam

def build_scene3_adventure():
    """Chapter 3: The Gooseberry Bush & The Blue Jacket Trapped in the Net."""
    reset_scene()
    
    mat_path = create_mat("M_CobblePath", (0.45, 0.42, 0.38), roughness=0.88)
    mat_net = create_mat("M_Netting", (0.85, 0.82, 0.70), roughness=0.6)
    mat_coat = create_mat("M_TrappedCoat", (0.10, 0.35, 0.85), roughness=0.45)
    mat_gold = create_mat("M_GoldButtons", (0.95, 0.78, 0.18), roughness=0.25, metallic=0.9)
    
    # 1. Ground Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    ground = bpy.context.active_object
    ground.name = "Adventure_Ground"
    ground.data.materials.append(mat_path)
    
    # 2. Real Gooseberry Bush (BushBerries_1.glb)
    bush_objs = import_glb_part(BUSH_SRC, "GooseberryBush")
    if bush_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-0.6, 0.4, 0.0))
        bush_root = bpy.context.active_object
        bush_root.name = "Bush_Root"
        bush_root.scale = (1.1, 1.1, 1.1)
        for o in bush_objs:
            if o != bush_root: o.parent = bush_root
            
    # 3. Wooden Fence with Perched Bird
    for fx, frot in [(-1.2, 0), (0.3, 15)]:
        f_objs = import_glb_part(FENCE_SRC, "Fence")
        if f_objs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(fx, 1.3, 0.0))
            f_root = bpy.context.active_object
            f_root.scale = (1.2, 1.2, 1.2)
            f_root.rotation_euler = (0, 0, math.radians(frot))
            for o in f_objs:
                if o != f_root: o.parent = f_root
                
    # Bird on fence post with proper Robin colors
    bird_objs = import_glb_part(CROW_SRC, "Robin")
    if bird_objs:
        mat_robin_feather = create_mat("M_RobinFeather", (0.20, 0.20, 0.22), roughness=0.7)
        mat_robin_chest = create_mat("M_RobinChest", (0.88, 0.38, 0.12), roughness=0.6)
        mat_robin_beak = create_mat("M_RobinBeak", (0.95, 0.68, 0.15), roughness=0.4)
        for o in bird_objs:
            if o.type == 'MESH':
                o.data.materials.clear()
                n = o.name.lower()
                if 'head' in n or 'jaw' in n:
                    o.data.materials.append(mat_robin_beak)
                elif 'neck' in n:
                    o.data.materials.append(mat_robin_chest)
                else:
                    o.data.materials.append(mat_robin_feather)
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.45, 1.2, 0.85))
        bird_root = bpy.context.active_object
        bird_root.name = "Robin_Bird"
        bird_root.scale = (0.32, 0.32, 0.32)
        bird_root.rotation_euler = (0, 0, math.radians(-40))
        for o in bird_objs:
            if o != bird_root: o.parent = bird_root

    # 4. Trapped Blue Jacket on the bush
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.26, depth=0.45, location=(-0.25, 0.15, 0.85))
    coat = bpy.context.active_object
    coat.name = "Trapped_Blue_Jacket"
    coat.rotation_euler = (math.radians(35), math.radians(25), math.radians(-15))
    coat.data.materials.append(mat_coat)
    
    for i, bz in enumerate([0.95, 0.85, 0.75]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-0.16, 0.08, bz))
        btn = bpy.context.active_object
        btn.name = f"Trapped_Button_{i}"
        btn.data.materials.append(mat_gold)
        
    # Netting loop
    bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.03, location=(-0.25, 0.15, 0.85))
    net = bpy.context.active_object
    net.rotation_euler = (math.radians(45), math.radians(20), 0)
    net.data.materials.append(mat_net)

    # 5. Wildflowers and Garden Rock
    flw_objs = import_glb_part(FLOWERS_SRC, "Wildflowers")
    if flw_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.0, 0.3, 0.0))
        flw_root = bpy.context.active_object
        flw_root.scale = (0.85, 0.85, 0.85)
        for o in flw_objs:
            if o != flw_root: o.parent = flw_root
            
    rock_objs = import_glb_part(ROCK_SRC, "MossRock")
    if rock_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-1.2, -0.6, 0.0))
        rock_root = bpy.context.active_object
        rock_root.scale = (1.3, 1.3, 1.3)
        for o in rock_objs:
            if o != rock_root: o.parent = rock_root

    # 6. Escaping Peter Rabbit (running fast without his jacket)
    load_and_style_peter(
        location=(0.4, -0.5, 0.0),
        scale=(0.30, 0.30, 0.30),
        rotation=(0, 0, math.radians(-45)),
        has_coat=False,
        pose="standing",
        name_prefix="Peter_Escaping"
    )
    
    # Lighting & Camera
    bpy.ops.object.light_add(type='SUN', location=(3.5, -4.0, 5.5))
    sun = bpy.context.active_object
    sun.data.energy = 2.2
    sun.data.color = (1.0, 0.96, 0.88)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    
    bpy.ops.object.camera_add(location=(0.0, -4.6, 2.4))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(67), 0, 0)
    cam.data.lens = 38
    bpy.context.scene.camera = cam

def build_scene4_bedtime():
    """Chapter 4: Bedtime, Cozy Sleep & Chamomile Tea."""
    reset_scene()
    
    mat_floor = create_mat("M_NightFloor", (0.16, 0.14, 0.18), roughness=0.85)
    mat_wall = create_mat("M_NightWall", (0.12, 0.12, 0.16), roughness=0.9)
    mat_sky = create_mat("M_NightSky", (0.04, 0.06, 0.12), roughness=0.2, emission=(0.04, 0.06, 0.12), emission_strength=1.5)
    mat_moon = create_mat("M_CrescentMoon", (0.95, 0.95, 0.75), roughness=0.2, emission=(0.95, 0.95, 0.75), emission_strength=4.0)
    mat_star = create_mat("M_Star", (1.0, 1.0, 0.9), roughness=0.1, emission=(1.0, 1.0, 0.9), emission_strength=6.0)
    mat_cup = create_mat("M_TeaMug", (0.94, 0.95, 0.96), roughness=0.2)
    mat_tea = create_mat("M_ChamomileTea", (0.95, 0.75, 0.25), roughness=0.3, emission=(0.95, 0.75, 0.25), emission_strength=2.5)
    mat_flame = create_mat("M_CandleFlame", (1.0, 0.75, 0.25), roughness=0.1, emission=(1.0, 0.7, 0.2), emission_strength=8.0)
    
    # 1. Room Floor
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    floor = bpy.context.active_object
    floor.name = "Bedtime_Floor"
    floor.data.materials.append(mat_floor)
    
    # 2. Back Wall with Moonlit Arch Window
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.4, 1.2))
    wall = bpy.context.active_object
    wall.scale = (3.2, 0.15, 2.4)
    wall.data.materials.append(mat_wall)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.65, depth=0.08, location=(0, 1.35, 1.5))
    window = bpy.context.active_object
    window.rotation_euler = (math.radians(90), 0, 0)
    window.data.materials.append(mat_sky)
    
    # Crescent Moon & Stars
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.07, location=(0.15, 1.28, 1.65))
    moon = bpy.context.active_object
    moon.scale = (1.0, 0.3, 1.0)
    moon.rotation_euler = (math.radians(90), math.radians(35), 0)
    moon.data.materials.append(mat_moon)
    
    for sx, sz in [(-0.25, 1.8), (-0.1, 1.3), (0.35, 1.4), (0.28, 1.85)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=4, radius=0.03, location=(sx, 1.28, sz))
        star = bpy.context.active_object
        star.data.materials.append(mat_star)

    # 3. Real Cozy Bed (Bed_Single.glb)
    bed_objs = import_glb_part(BED_SRC, "Bed")
    if bed_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-0.45, 0.2, 0.0))
        bed_root = bpy.context.active_object
        bed_root.name = "Bed_Root"
        bed_root.scale = (0.85, 0.85, 0.85)
        bed_root.rotation_euler = (0, 0, math.radians(-10))
        for o in bed_objs:
            if o != bed_root: o.parent = bed_root

    # 4. Sleeping Peter tucked comfortably into bed (Resting on top of mattress at z=0.65)
    load_and_style_peter(
        location=(-0.45, 0.35, 0.65),
        scale=(0.28, 0.28, 0.28),
        rotation=(0, 0, math.radians(-25)),
        has_coat=False,
        pose="sleeping",
        name_prefix="Peter_Sleeping"
    )
    
    # 5. Nightstand Table (Table_RoundSmall.glb)
    tbl_objs = import_glb_part(TABLE_SRC, "Nightstand")
    if tbl_objs:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.15, 0.25, 0.0))
        tbl_root = bpy.context.active_object
        tbl_root.name = "Nightstand_Root"
        tbl_root.scale = (0.85, 0.85, 0.85)
        for o in tbl_objs:
            if o != tbl_root: o.parent = tbl_root
            
    # Chamomile Tea Mug on Nightstand
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.12, location=(1.05, 0.25, 0.62))
    mug = bpy.context.active_object
    mug.name = "Chamomile_Tea_Mug"
    mug.data.materials.append(mat_cup)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.07, depth=0.02, location=(1.05, 0.25, 0.67))
    tea = bpy.context.active_object
    tea.data.materials.append(mat_tea)
    
    # Candle holder & glowing flame
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.04, depth=0.08, location=(1.25, 0.35, 0.60))
    candle = bpy.context.active_object
    candle.data.materials.append(mat_cup)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(1.25, 0.35, 0.68))
    flame = bpy.context.active_object
    flame.data.materials.append(mat_flame)
    
    # Lighting & Camera
    bpy.ops.object.light_add(type='POINT', location=(1.25, 0.35, 0.82))
    candle_light = bpy.context.active_object
    candle_light.data.energy = 32.0
    candle_light.data.color = (1.0, 0.82, 0.45)
    
    bpy.ops.object.light_add(type='SUN', location=(-2, -4, 4))
    night_sun = bpy.context.active_object
    night_sun.data.energy = 1.2
    night_sun.data.color = (0.65, 0.78, 0.98)
    night_sun.rotation_euler = (math.radians(50), 0, math.radians(-25))
    
    bpy.ops.object.camera_add(location=(0.0, -4.5, 2.3))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(68), 0, 0)
    cam.data.lens = 38
    bpy.context.scene.camera = cam

def export_active_scene_glb(filepath):
    """Exports current active scene to web-ready GLB without duplicate lights."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_materials='EXPORT',
        export_cameras=True,
        export_lights=False, # Three.js handles scene lighting cleanly
        export_yup=True
    )
    size_kb = os.path.getsize(filepath) / 1024
    print(f"Exported: {filepath} ({size_kb:.1f} KB)")
    return size_kb

def render_preview(filepath):
    """Renders preview illustration."""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath
    scene.render.engine = 'BLENDER_EEVEE'
    bpy.ops.render.render(write_still=True)
    print(f"Rendered preview: {filepath}")

def main():
    print("=== Generating High-Fidelity 3D Storybook Assets for Peter Rabbit ===")
    manifest = {}
    
    # 1. Standalone Peter Rabbit
    reset_scene()
    load_and_style_peter(location=(0,0,0), scale=(0.5, 0.5, 0.5), has_coat=True, name_prefix="Peter_Master")
    peter_path = os.path.join(MODELS_DIR, "peter_rabbit.glb")
    manifest["peter_rabbit"] = {"path": peter_path, "size_kb": export_active_scene_glb(peter_path)}
    
    # 2. Chapter 1: The Burrow
    build_scene1_burrow()
    c1_model = os.path.join(MODELS_DIR, "scene1_burrow.glb")
    manifest["scene1_burrow"] = {"path": c1_model, "size_kb": export_active_scene_glb(c1_model)}
    c1_render = os.path.join(RENDERS_DIR, "chapter1_burrow.png")
    render_preview(c1_render)
    
    # 3. Chapter 2: The Garden
    build_scene2_garden()
    c2_model = os.path.join(MODELS_DIR, "scene2_garden.glb")
    manifest["scene2_garden"] = {"path": c2_model, "size_kb": export_active_scene_glb(c2_model)}
    c2_render = os.path.join(RENDERS_DIR, "chapter2_garden.png")
    render_preview(c2_render)
    
    # Render High-Res Book Cover
    render_preview(os.path.join(RENDERS_DIR, "book_cover.png"))
    
    # 4. Chapter 3: The Adventure
    build_scene3_adventure()
    c3_model = os.path.join(MODELS_DIR, "scene3_adventure.glb")
    manifest["scene3_adventure"] = {"path": c3_model, "size_kb": export_active_scene_glb(c3_model)}
    c3_render = os.path.join(RENDERS_DIR, "chapter3_adventure.png")
    render_preview(c3_render)
    
    # 5. Chapter 4: Bedtime
    build_scene4_bedtime()
    c4_model = os.path.join(MODELS_DIR, "scene4_bedtime.glb")
    manifest["scene4_bedtime"] = {"path": c4_model, "size_kb": export_active_scene_glb(c4_model)}
    c4_render = os.path.join(RENDERS_DIR, "chapter4_bedtime.png")
    render_preview(c4_render)
    
    manifest_path = os.path.join(ASSETS_DIR, "assets_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print("=== All High-Quality 3D Storybook Assets Successfully Generated! ===")

if __name__ == "__main__":
    main()
