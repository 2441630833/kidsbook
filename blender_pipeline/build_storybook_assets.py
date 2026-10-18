"""
KidsBook 3D Asset Generator - The Tale of Peter Rabbit (Beatrix Potter, 1902 - Public Domain)
Procedurally builds stylized 3D storybook dioramas, characters, and assets in Blender,
exports optimized GLTF/GLB models for WebGL/Three.js, and renders high-res illustrations.
Compatible with Blender 4.x & 5.x.
"""
import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler, Color

# Output directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "assets", "models")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "assets", "renders")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

def reset_scene():
    """Clear all objects, meshes, materials, and lights."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if "Scene" not in bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.data.scenes[0]
    bpy.context.window.scene = scene
    return scene

def create_mat(name, base_color, roughness=0.55, metallic=0.0, emission=None, emission_strength=1.0):
    """Create a Principled BSDF material compatible with Blender 4.x / 5.x."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*base_color[:3], 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission[:3], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def create_peter_rabbit(location=(0,0,0), scale=(1,1,1), rotation=(0,0,0), pose="standing", has_coat=True, name_prefix="Peter"):
    """Builds a cute stylized Peter Rabbit character mesh collection."""
    coll = bpy.data.collections.new(f"{name_prefix}_Collection")
    bpy.context.scene.collection.children.link(coll)
    
    # Materials
    mat_fur = create_mat(f"{name_prefix}_Fur", (0.76, 0.58, 0.40), roughness=0.85) # Sandy brown
    mat_inner_ear = create_mat(f"{name_prefix}_InnerEar", (0.92, 0.65, 0.62), roughness=0.6)
    mat_white = create_mat(f"{name_prefix}_White", (0.95, 0.94, 0.90), roughness=0.8)
    mat_eyes = create_mat(f"{name_prefix}_Eyes", (0.05, 0.04, 0.04), roughness=0.1, metallic=0.2)
    mat_nose = create_mat(f"{name_prefix}_Nose", (0.85, 0.45, 0.45), roughness=0.5)
    mat_coat = create_mat(f"{name_prefix}_Coat", (0.15, 0.35, 0.65), roughness=0.5) # Iconic blue
    mat_brass = create_mat(f"{name_prefix}_Brass", (0.95, 0.75, 0.15), roughness=0.25, metallic=0.85)
    
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.32, location=(0, 0, 0.4))
    body = bpy.context.active_object
    body.name = f"{name_prefix}_Body"
    body.scale = (0.85, 0.75, 1.1)
    body.data.materials.append(mat_fur)
    coll.objects.link(body)
    bpy.context.scene.collection.objects.unlink(body)
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.24, location=(0, -0.05, 0.78))
    head = bpy.context.active_object
    head.name = f"{name_prefix}_Head"
    head.scale = (0.95, 0.9, 0.95)
    head.data.materials.append(mat_fur)
    coll.objects.link(head)
    bpy.context.scene.collection.objects.unlink(head)
    
    # Ears
    for side, mult in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.12, location=(0.09 * mult, -0.02, 1.08))
        ear = bpy.context.active_object
        ear.name = f"{name_prefix}_Ear_{side}"
        ear.scale = (0.35, 0.2, 1.6)
        ear.rotation_euler = (math.radians(-10), math.radians(12 * mult), math.radians(5 * mult))
        ear.data.materials.append(mat_fur)
        coll.objects.link(ear)
        bpy.context.scene.collection.objects.unlink(ear)
        
        # Inner ear
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.09, location=(0.09 * mult, -0.04, 1.08))
        inear = bpy.context.active_object
        inear.name = f"{name_prefix}_InEar_{side}"
        inear.scale = (0.25, 0.1, 1.3)
        inear.rotation_euler = ear.rotation_euler
        inear.data.materials.append(mat_inner_ear)
        coll.objects.link(inear)
        bpy.context.scene.collection.objects.unlink(inear)
    
    # Eyes
    for side, mult in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.035, location=(0.11 * mult, -0.23, 0.82))
        eye = bpy.context.active_object
        eye.name = f"{name_prefix}_Eye_{side}"
        eye.data.materials.append(mat_eyes)
        coll.objects.link(eye)
        bpy.context.scene.collection.objects.unlink(eye)
        
    # Nose
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.03, location=(0, -0.28, 0.77))
    nose = bpy.context.active_object
    nose.name = f"{name_prefix}_Nose"
    nose.data.materials.append(mat_nose)
    coll.objects.link(nose)
    bpy.context.scene.collection.objects.unlink(nose)
    
    # Fluffy tail
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.09, location=(0, 0.28, 0.25))
    tail = bpy.context.active_object
    tail.name = f"{name_prefix}_Tail"
    tail.data.materials.append(mat_white)
    coll.objects.link(tail)
    bpy.context.scene.collection.objects.unlink(tail)
    
    # Feet
    for side, mult in [("L", 1), ("R", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.1, location=(0.14 * mult, -0.06, 0.08))
        foot = bpy.context.active_object
        foot.name = f"{name_prefix}_Foot_{side}"
        foot.scale = (0.6, 1.3, 0.4)
        foot.data.materials.append(mat_fur)
        coll.objects.link(foot)
        bpy.context.scene.collection.objects.unlink(foot)
        
    # Blue Jacket
    if has_coat:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.34, depth=0.42, location=(0, -0.01, 0.44))
        coat = bpy.context.active_object
        coat.name = f"{name_prefix}_BlueJacket"
        coat.scale = (0.9, 0.82, 1.0)
        coat.data.materials.append(mat_coat)
        coll.objects.link(coat)
        bpy.context.scene.collection.objects.unlink(coat)
        
        # Brass Buttons
        for b_z in [0.52, 0.44, 0.36]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025, location=(0, -0.28, b_z))
            btn = bpy.context.active_object
            btn.name = f"{name_prefix}_BrassButton"
            btn.data.materials.append(mat_brass)
            coll.objects.link(btn)
            bpy.context.scene.collection.objects.unlink(btn)
            
    # Parent all parts to an empty root
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"{name_prefix}_Root"
    coll.objects.link(root)
    bpy.context.scene.collection.objects.unlink(root)
    
    for obj in list(coll.objects):
        if obj != root:
            obj.parent = root
            
    root.location = location
    root.scale = scale
    root.rotation_euler = Euler(rotation, 'XYZ')
    return root, coll

def build_scene1_burrow():
    """Chapter 1: The Cozy Burrow under the Giant Fir Tree."""
    reset_scene()
    
    # Palette
    mat_earth = create_mat("M_Earth", (0.35, 0.22, 0.14), roughness=0.9)
    mat_wood = create_mat("M_Wood", (0.52, 0.32, 0.18), roughness=0.7)
    mat_table = create_mat("M_Table", (0.65, 0.42, 0.22), roughness=0.6)
    mat_teapot = create_mat("M_Teapot", (0.92, 0.94, 0.95), roughness=0.2)
    mat_lantern_brass = create_mat("M_LanternBrass", (0.85, 0.7, 0.25), roughness=0.3, metallic=0.8)
    mat_lantern_light = create_mat("M_LanternGlow", (1.0, 0.85, 0.4), roughness=0.1, emission=(1.0, 0.8, 0.35), emission_strength=5.0)
    mat_quilt = create_mat("M_Quilt", (0.85, 0.35, 0.3), roughness=0.8)
    mat_pillow = create_mat("M_Pillow", (0.95, 0.95, 0.92), roughness=0.9)
    mat_bark = create_mat("M_Bark", (0.28, 0.18, 0.12), roughness=0.95)
    
    # Earthen Base / Floor
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.5, depth=0.3, location=(0, 0, -0.15))
    floor = bpy.context.active_object
    floor.name = "Burrow_Floor"
    floor.data.materials.append(mat_earth)
    
    # Giant Fir Tree Trunk Arch & Roots
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.9, depth=2.8, location=(-1.2, 0.8, 1.2))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Trunk"
    trunk.rotation_euler = (math.radians(10), math.radians(-15), 0)
    trunk.data.materials.append(mat_bark)
    
    # Root Arch over burrow
    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.22, major_segments=24, minor_segments=12, location=(0, 0.5, 0.8))
    arch = bpy.context.active_object
    arch.name = "Tree_Root_Arch"
    arch.scale = (1.2, 0.6, 1.0)
    arch.rotation_euler = (math.radians(65), 0, math.radians(20))
    arch.data.materials.append(mat_bark)
    
    # Wooden Rustic Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.0, -0.7, 0.2))
    bed_frame = bpy.context.active_object
    bed_frame.name = "Bed_Frame"
    bed_frame.scale = (0.65, 1.1, 0.22)
    bed_frame.data.materials.append(mat_wood)
    
    # Quilt
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.0, -0.6, 0.35))
    quilt = bpy.context.active_object
    quilt.name = "Bed_Quilt"
    quilt.scale = (0.6, 0.7, 0.12)
    quilt.data.materials.append(mat_quilt)
    
    # Pillow
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(-1.0, -1.05, 0.38))
    pillow = bpy.context.active_object
    pillow.name = "Bed_Pillow"
    pillow.scale = (1.4, 0.9, 0.4)
    pillow.data.materials.append(mat_pillow)
    
    # Wooden Table
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.06, location=(0.8, -0.4, 0.45))
    table_top = bpy.context.active_object
    table_top.name = "Table_Top"
    table_top.data.materials.append(mat_table)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.45, location=(0.8, -0.4, 0.225))
    table_leg = bpy.context.active_object
    table_leg.name = "Table_Leg"
    table_leg.data.materials.append(mat_table)
    
    # Teapot on table
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.8, -0.4, 0.58))
    pot = bpy.context.active_object
    pot.name = "Teapot_Body"
    pot.data.materials.append(mat_teapot)
    
    # Teacup
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.04, depth=0.06, location=(0.95, -0.28, 0.51))
    cup = bpy.context.active_object
    cup.name = "Teacup"
    cup.data.materials.append(mat_teapot)
    
    # Wooden Stool
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.05, location=(0.7, 0.25, 0.28))
    stool = bpy.context.active_object
    stool.name = "Stool_Seat"
    stool.data.materials.append(mat_wood)
    
    # Warm Hanging Lantern
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=0.2, location=(0.1, -0.2, 1.4))
    lantern = bpy.context.active_object
    lantern.name = "Lantern_Glass"
    lantern.data.materials.append(mat_lantern_light)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=0.04, location=(0.1, -0.2, 1.52))
    lantern_cap = bpy.context.active_object
    lantern_cap.name = "Lantern_Cap"
    lantern_cap.data.materials.append(mat_lantern_brass)
    
    # Lantern Point Light
    bpy.ops.object.light_add(type='POINT', radius=0.3, location=(0.1, -0.2, 1.35))
    light = bpy.context.active_object
    light.name = "Lantern_Light"
    light.data.energy = 25.0
    light.data.color = (1.0, 0.82, 0.45)
    
    # Peter Rabbit standing in the burrow
    create_peter_rabbit(location=(0.1, -0.4, 0.0), scale=(0.7, 0.7, 0.7), rotation=(0, 0, math.radians(20)), has_coat=True, name_prefix="Peter_Burrow")
    
    # Warm sunbeam through burrow entrance
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 4))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.data.color = (1.0, 0.95, 0.85)
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(-35))
    
    # Camera setup
    bpy.ops.object.camera_add(location=(1.8, -3.2, 1.9))
    cam = bpy.context.active_object
    cam.name = "Burrow_Camera"
    cam.rotation_euler = (math.radians(65), 0, math.radians(28))
    cam.data.lens = 42
    bpy.context.scene.camera = cam

def build_scene2_garden():
    """Chapter 2: Mr. McGregor's Secret Garden with Carrots and Watering Can."""
    reset_scene()
    
    # Materials
    mat_grass = create_mat("M_Grass", (0.32, 0.62, 0.22), roughness=0.85)
    mat_soil = create_mat("M_Soil", (0.38, 0.25, 0.15), roughness=0.95)
    mat_carrot = create_mat("M_Carrot", (0.95, 0.40, 0.05), roughness=0.45)
    mat_leaves = create_mat("M_CarrotLeaves", (0.22, 0.72, 0.18), roughness=0.6)
    mat_cabbage = create_mat("M_Cabbage", (0.55, 0.78, 0.32), roughness=0.7)
    mat_can = create_mat("M_WaterCan", (0.82, 0.18, 0.14), roughness=0.35) # Red watering can
    mat_metal = create_mat("M_Zinc", (0.75, 0.80, 0.82), roughness=0.3, metallic=0.8)
    mat_fence = create_mat("M_Fence", (0.88, 0.86, 0.80), roughness=0.65) # White picket fence
    
    # Garden Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    ground = bpy.context.active_object
    ground.name = "Garden_Ground"
    ground.data.materials.append(mat_grass)
    
    # Vegetable Raised Soil Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, 0.2, 0.1))
    soil_bed = bpy.context.active_object
    soil_bed.name = "Soil_Bed"
    soil_bed.scale = (1.4, 2.0, 0.2)
    soil_bed.data.materials.append(mat_soil)
    
    # Carrots in rows
    carrot_coords = [
        (-1.0, -0.5), (-0.6, -0.5), (-0.2, -0.5),
        (-1.0, 0.1),  (-0.6, 0.1),  (-0.2, 0.1),
        (-1.0, 0.7),  (-0.6, 0.7),  (-0.2, 0.7)
    ]
    for i, (cx, cy) in enumerate(carrot_coords):
        # Carrot root sticking up
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.07, depth=0.28, location=(cx, cy, 0.25))
        c_root = bpy.context.active_object
        c_root.name = f"Carrot_Root_{i}"
        c_root.rotation_euler = (math.radians(180), 0, 0)
        c_root.data.materials.append(mat_carrot)
        
        # Feather leaf crown
        for lf_idx in range(4):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.18, location=(cx, cy, 0.42))
            c_leaf = bpy.context.active_object
            c_leaf.name = f"Carrot_Leaf_{i}_{lf_idx}"
            c_leaf.scale = (0.5, 1.0, 1.2)
            c_leaf.rotation_euler = (math.radians(20 + lf_idx * 5), math.radians(lf_idx * 90), 0)
            c_leaf.data.materials.append(mat_leaves)
            
    # Cabbages on the right
    cabbage_coords = [(0.6, -0.6), (0.7, 0.0), (0.8, 0.6)]
    for i, (cbx, cby) in enumerate(cabbage_coords):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.22, location=(cbx, cby, 0.18))
        cab = bpy.context.active_object
        cab.name = f"Cabbage_{i}"
        cab.scale = (1.1, 1.1, 0.8)
        cab.data.materials.append(mat_cabbage)
        
    # The Classic Red Watering Can
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.22, depth=0.36, location=(1.2, -0.7, 0.18))
    can_body = bpy.context.active_object
    can_body.name = "WaterCan_Body"
    can_body.data.materials.append(mat_can)
    
    # Spout
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045, depth=0.38, location=(1.05, -0.9, 0.28))
    spout = bpy.context.active_object
    spout.name = "WaterCan_Spout"
    spout.rotation_euler = (math.radians(45), 0, math.radians(-30))
    spout.data.materials.append(mat_metal)
    
    # Rose sprinkler head
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.09, depth=0.06, location=(0.95, -1.02, 0.41))
    rose = bpy.context.active_object
    rose.name = "WaterCan_Rose"
    rose.rotation_euler = (math.radians(45), 0, math.radians(-30))
    rose.data.materials.append(mat_metal)
    
    # Handle
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.025, location=(1.35, -0.55, 0.25))
    handle = bpy.context.active_object
    handle.name = "WaterCan_Handle"
    handle.rotation_euler = (math.radians(90), math.radians(25), 0)
    handle.data.materials.append(mat_can)
    
    # White Picket Fence in background
    for p in range(6):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.5 + p * 0.6, 1.4, 0.5))
        picket = bpy.context.active_object
        picket.name = f"Fence_Picket_{p}"
        picket.scale = (0.1, 0.04, 0.9)
        picket.data.materials.append(mat_fence)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 1.38, 0.4))
    rail = bpy.context.active_object
    rail.name = "Fence_Rail"
    rail.scale = (3.4, 0.04, 0.08)
    rail.data.materials.append(mat_fence)
    
    # Peter Rabbit joyfully munching a freshly pulled carrot!
    create_peter_rabbit(location=(-0.6, -0.9, 0.0), scale=(0.7, 0.7, 0.7), rotation=(0, 0, math.radians(-35)), has_coat=True, name_prefix="Peter_Garden")
    
    # Held carrot in Peter's paws
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.05, depth=0.22, location=(-0.56, -0.97, 0.35))
    held_carrot = bpy.context.active_object
    held_carrot.name = "Held_Carrot"
    held_carrot.rotation_euler = (math.radians(65), math.radians(30), 0)
    held_carrot.data.materials.append(mat_carrot)
    
    # Sunlight & Warm Garden Lighting
    bpy.ops.object.light_add(type='SUN', location=(3.0, -3.0, 5.0))
    sun = bpy.context.active_object
    sun.data.energy = 3.5
    sun.data.color = (1.0, 0.96, 0.88)
    sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(-40))
    
    # Sky fill light
    bpy.ops.object.light_add(type='POINT', radius=1.0, location=(-1.5, 1.5, 2.5))
    sky_fill = bpy.context.active_object
    sky_fill.data.energy = 15.0
    sky_fill.data.color = (0.7, 0.85, 1.0)
    
    # Camera
    bpy.ops.object.camera_add(location=(1.5, -3.4, 2.1))
    cam = bpy.context.active_object
    cam.name = "Garden_Camera"
    cam.rotation_euler = (math.radians(64), 0, math.radians(24))
    cam.data.lens = 45
    bpy.context.scene.camera = cam

def build_scene3_adventure():
    """Chapter 3: The Gooseberry Bush & The Blue Jacket Trapped in the Net."""
    reset_scene()
    
    # Materials
    mat_path = create_mat("M_CobblePath", (0.65, 0.62, 0.58), roughness=0.9)
    mat_bush = create_mat("M_GooseberryBush", (0.20, 0.55, 0.22), roughness=0.75)
    mat_berries = create_mat("M_Berries", (0.75, 0.15, 0.25), roughness=0.3)
    mat_net = create_mat("M_Netting", (0.85, 0.82, 0.70), roughness=0.6)
    mat_coat = create_mat("M_TrappedCoat", (0.15, 0.35, 0.65), roughness=0.55)
    mat_gold = create_mat("M_GoldButtons", (0.95, 0.75, 0.15), roughness=0.25, metallic=0.9)
    mat_cart = create_mat("M_Wheelbarrow", (0.55, 0.35, 0.20), roughness=0.7)
    mat_wheel = create_mat("M_IronWheel", (0.25, 0.25, 0.28), roughness=0.4, metallic=0.7)
    mat_bird = create_mat("M_Bluebird", (0.25, 0.50, 0.85), roughness=0.5)
    mat_bird_beak = create_mat("M_Beak", (0.95, 0.65, 0.1), roughness=0.4)
    
    # Ground Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    ground = bpy.context.active_object
    ground.name = "Adventure_Ground"
    ground.data.materials.append(mat_path)
    
    # Big Gooseberry Bush
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.9, location=(-0.6, 0.4, 0.6))
    bush1 = bpy.context.active_object
    bush1.name = "Gooseberry_Bush_Main"
    bush1.scale = (1.1, 0.9, 0.85)
    bush1.data.materials.append(mat_bush)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.6, location=(-1.1, 0.2, 0.45))
    bush2 = bpy.context.active_object
    bush2.name = "Gooseberry_Bush_Sub"
    bush2.scale = (0.9, 0.9, 0.7)
    bush2.data.materials.append(mat_bush)
    
    # Gooseberries hanging
    for i, (bx, by, bz) in enumerate([
        (-0.3, 0.1, 0.7), (-0.5, 0.0, 0.5), (-0.8, -0.1, 0.6),
        (-0.2, 0.5, 0.8), (-0.9, 0.7, 0.55), (-0.4, 0.8, 0.4)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.065, location=(bx, by, bz))
        berry = bpy.context.active_object
        berry.name = f"Gooseberry_{i}"
        berry.data.materials.append(mat_berries)
        
    # The Netting over the bush
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.04, location=(-0.6, 0.4, 0.7))
    net1 = bpy.context.active_object
    net1.name = "Gooseberry_Net_Rope"
    net1.rotation_euler = (math.radians(35), math.radians(20), 0)
    net1.data.materials.append(mat_net)
    
    # The Trapped Little Blue Jacket caught on the net!
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.24, depth=0.38, location=(-0.15, 0.1, 0.75))
    coat = bpy.context.active_object
    coat.name = "Trapped_Blue_Jacket"
    coat.rotation_euler = (math.radians(35), math.radians(25), math.radians(-15))
    coat.data.materials.append(mat_coat)
    
    # Brass button caught by twig
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.038, location=(-0.12, 0.05, 0.82))
    btn = bpy.context.active_object
    btn.name = "Trapped_Brass_Button"
    btn.data.materials.append(mat_gold)
    
    # Peter Rabbit having slipped out, running swiftly without his jacket!
    create_peter_rabbit(location=(0.8, -0.6, 0.0), scale=(0.65, 0.65, 0.65), rotation=(0, 0, math.radians(70)), has_coat=False, name_prefix="Peter_Escaping")
    
    # Wooden Wheelbarrow
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.1, 0.7, 0.35))
    wb_body = bpy.context.active_object
    wb_body.name = "Wheelbarrow_Body"
    wb_body.scale = (0.4, 0.7, 0.2)
    wb_body.rotation_euler = (0, 0, math.radians(-25))
    wb_body.data.materials.append(mat_cart)
    
    # Wheelbarrow wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=0.05, location=(1.35, 1.15, 0.18))
    wb_wheel = bpy.context.active_object
    wb_wheel.name = "Wheelbarrow_Wheel"
    wb_wheel.rotation_euler = (0, math.radians(90), math.radians(-25))
    wb_wheel.data.materials.append(mat_wheel)
    
    # Friendly Robin perched atop fence post
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.9, location=(-1.4, -0.8, 0.45))
    post = bpy.context.active_object
    post.name = "Fence_Post"
    post.data.materials.append(mat_cart)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.08, location=(-1.4, -0.8, 0.96))
    bird = bpy.context.active_object
    bird.name = "Robin_Body"
    bird.scale = (0.7, 1.0, 0.8)
    bird.data.materials.append(mat_bird)
    
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.025, depth=0.06, location=(-1.4, -0.9, 0.97))
    beak = bpy.context.active_object
    beak.name = "Robin_Beak"
    beak.rotation_euler = (math.radians(-90), 0, 0)
    beak.data.materials.append(mat_bird_beak)
    
    # Lighting
    bpy.ops.object.light_add(type='SUN', location=(3.0, -3.0, 5.0))
    sun = bpy.context.active_object
    sun.data.energy = 3.2
    sun.data.color = (1.0, 0.95, 0.85)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-30))
    
    # Camera
    bpy.ops.object.camera_add(location=(1.7, -3.2, 2.0))
    cam = bpy.context.active_object
    cam.name = "Adventure_Camera"
    cam.rotation_euler = (math.radians(65), 0, math.radians(26))
    cam.data.lens = 45
    bpy.context.scene.camera = cam

def build_scene4_bedtime():
    """Chapter 4: Safe at Home, Warm Chamomile Tea and Bedtime."""
    reset_scene()
    
    # Materials
    mat_floor = create_mat("M_NightFloor", (0.35, 0.28, 0.22), roughness=0.8)
    mat_wall = create_mat("M_NightWall", (0.18, 0.16, 0.25), roughness=0.9)
    mat_sky = create_mat("M_NightSky", (0.05, 0.06, 0.14), roughness=0.9)
    mat_moon = create_mat("M_Moon", (1.0, 0.95, 0.7), roughness=0.2, emission=(1.0, 0.95, 0.65), emission_strength=4.0)
    mat_star = create_mat("M_Star", (1.0, 1.0, 0.9), roughness=0.1, emission=(1.0, 1.0, 0.9), emission_strength=6.0)
    mat_bed = create_mat("M_BedWood", (0.45, 0.28, 0.16), roughness=0.6)
    mat_blanket = create_mat("M_SoftBlanket", (0.85, 0.72, 0.65), roughness=0.9) # Warm cozy cream
    mat_cup = create_mat("M_TeaMug", (0.94, 0.95, 0.96), roughness=0.2)
    mat_tea = create_mat("M_ChamomileTea", (0.85, 0.65, 0.2), roughness=0.3, emission=(0.85, 0.65, 0.2), emission_strength=1.5)
    mat_candle = create_mat("M_CandleFlame", (1.0, 0.75, 0.25), roughness=0.1, emission=(1.0, 0.7, 0.2), emission_strength=8.0)
    mat_wax = create_mat("M_CandleWax", (0.92, 0.88, 0.80), roughness=0.4)
    
    # Room Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.6, depth=0.3, location=(0, 0, -0.15))
    room_floor = bpy.context.active_object
    room_floor.name = "Bedtime_Floor"
    room_floor.data.materials.append(mat_floor)
    
    # Back Cottage Wall with Arched Window
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.4, 1.2))
    wall = bpy.context.active_object
    wall.name = "Cottage_Wall"
    wall.scale = (3.2, 0.15, 2.4)
    wall.data.materials.append(mat_wall)
    
    # Arched Window Pane (Night Sky)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.65, depth=0.08, location=(0, 1.35, 1.5))
    window = bpy.context.active_object
    window.name = "Window_Pane"
    window.rotation_euler = (math.radians(90), 0, 0)
    window.data.materials.append(mat_sky)
    
    # Glowing Crescent Moon
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.07, location=(0.15, 1.28, 1.65))
    moon = bpy.context.active_object
    moon.name = "Crescent_Moon"
    moon.scale = (1.0, 0.3, 1.0)
    moon.rotation_euler = (math.radians(90), math.radians(35), 0)
    moon.data.materials.append(mat_moon)
    
    # Little Stars in window
    for s_idx, (sx, sz) in enumerate([(-0.25, 1.8), (-0.1, 1.3), (0.35, 1.4), (0.28, 1.85)]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=4, radius=0.03, location=(sx, 1.28, sz))
        star = bpy.context.active_object
        star.name = f"Star_{s_idx}"
        star.data.materials.append(mat_star)
        
    # Cozy Bed
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, -0.2, 0.25))
    bed = bpy.context.active_object
    bed.name = "Bed_Frame"
    bed.scale = (1.4, 0.9, 0.25)
    bed.data.materials.append(mat_bed)
    
    # Soft Blanket tucked in
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.35, -0.2, 0.42))
    blanket = bpy.context.active_object
    blanket.name = "Bed_Blanket"
    blanket.scale = (1.0, 0.85, 0.18)
    blanket.data.materials.append(mat_blanket)
    
    # Fluffy Pillow
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.24, location=(-1.0, -0.2, 0.48))
    pillow = bpy.context.active_object
    pillow.name = "Bed_Pillow"
    pillow.scale = (0.7, 1.3, 0.45)
    pillow.data.materials.append(mat_blanket)
    
    # Peter Rabbit curled up sleeping peacefully in bed!
    # Sleeping bunny: rotated onto side, head nestled on pillow
    peter_root, peter_coll = create_peter_rabbit(location=(-0.75, -0.2, 0.38), scale=(0.55, 0.55, 0.55), rotation=(math.radians(20), math.radians(-15), math.radians(75)), has_coat=False, name_prefix="Peter_Sleeping")
    
    # Bedside Wooden Table
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.35, depth=0.06, location=(0.7, -0.4, 0.4))
    nightstand = bpy.context.active_object
    nightstand.name = "Nightstand_Top"
    nightstand.data.materials.append(mat_bed)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=0.4, location=(0.7, -0.4, 0.2))
    nightstand_leg = bpy.context.active_object
    nightstand_leg.name = "Nightstand_Leg"
    nightstand_leg.data.materials.append(mat_bed)
    
    # Steaming Cup of Chamomile Tea
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.14, location=(0.62, -0.35, 0.5))
    tea_mug = bpy.context.active_object
    tea_mug.name = "Chamomile_Tea_Mug"
    tea_mug.data.materials.append(mat_cup)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.02, location=(0.62, -0.35, 0.55))
    tea_liq = bpy.context.active_object
    tea_liq.name = "Chamomile_Tea_Liquid"
    tea_liq.data.materials.append(mat_tea)
    
    # Bedside Candle casting soft warm amber light
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.04, depth=0.12, location=(0.78, -0.48, 0.49))
    wax = bpy.context.active_object
    wax.name = "Candle_Wax"
    wax.data.materials.append(mat_wax)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025, location=(0.78, -0.48, 0.58))
    flame = bpy.context.active_object
    flame.name = "Candle_Flame"
    flame.scale = (0.7, 0.7, 1.5)
    flame.data.materials.append(mat_candle)
    
    # Warm Candle Point Light
    bpy.ops.object.light_add(type='POINT', radius=0.4, location=(0.78, -0.48, 0.62))
    light = bpy.context.active_object
    light.name = "Candle_Light"
    light.data.energy = 18.0
    light.data.color = (1.0, 0.78, 0.42)
    
    # Soft Moonlight through window
    bpy.ops.object.light_add(type='POINT', radius=0.8, location=(0.1, 1.1, 1.6))
    moonlight = bpy.context.active_object
    moonlight.name = "Moon_Light"
    moonlight.data.energy = 8.0
    moonlight.data.color = (0.65, 0.78, 1.0)
    
    # Camera
    bpy.ops.object.camera_add(location=(1.5, -3.2, 1.9))
    cam = bpy.context.active_object
    cam.name = "Bedtime_Camera"
    cam.rotation_euler = (math.radians(66), 0, math.radians(24))
    cam.data.lens = 45
    bpy.context.scene.camera = cam

def build_master_book():
    """Builds a classic 3D Hardcover Pop-up Book base."""
    reset_scene()
    
    mat_cover = create_mat("M_BookCover", (0.12, 0.28, 0.48), roughness=0.35) # Deep navy cloth
    mat_gold_foil = create_mat("M_GoldFoil", (0.95, 0.78, 0.2), roughness=0.2, metallic=0.9)
    mat_page = create_mat("M_BookPaper", (0.96, 0.94, 0.88), roughness=0.9) # Vintage parchment
    
    # Left Cover
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 0, 0))
    cov_l = bpy.context.active_object
    cov_l.name = "Book_Cover_Left"
    cov_l.scale = (2.2, 3.2, 0.08)
    cov_l.data.materials.append(mat_cover)
    
    # Right Cover
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.2, 0, 0))
    cov_r = bpy.context.active_object
    cov_r.name = "Book_Cover_Right"
    cov_r.scale = (2.2, 3.2, 0.08)
    cov_r.data.materials.append(mat_cover)
    
    # Book Spine
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=3.2, location=(0, 0, -0.04))
    spine = bpy.context.active_object
    spine.name = "Book_Spine"
    spine.scale = (0.6, 1.0, 1.0)
    spine.rotation_euler = (math.radians(90), 0, 0)
    spine.data.materials.append(mat_cover)
    
    # Left Page Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.15, 0, 0.07))
    page_l = bpy.context.active_object
    page_l.name = "Pages_Left"
    page_l.scale = (2.0, 3.0, 0.06)
    page_l.data.materials.append(mat_page)
    
    # Right Page Block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.15, 0, 0.07))
    page_r = bpy.context.active_object
    page_r.name = "Pages_Right"
    page_r.scale = (2.0, 3.0, 0.06)
    page_r.data.materials.append(mat_page)
    
    # Gold Foil Corner Trim
    for mx, my in [(-2.2, 1.5), (-2.2, -1.5), (2.2, 1.5), (2.2, -1.5)]:
        bpy.ops.mesh.primitive_cube_add(size=0.25, location=(mx, my, 0.05))
        corner = bpy.context.active_object
        corner.name = "Gold_Corner"
        corner.scale = (1.0, 1.0, 0.2)
        corner.data.materials.append(mat_gold_foil)

def export_active_scene_glb(filepath):
    """Exports current active Blender scene to a web-optimized GLB file."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_materials='EXPORT',
        export_cameras=True,
        export_lights=True,
        export_yup=True
    )
    size_kb = os.path.getsize(filepath) / 1024
    print(f"Exported: {filepath} ({size_kb:.1f} KB)")
    return size_kb

def render_preview(filepath):
    """Renders high-quality preview frame for the scene."""
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath
    
    # Workbench / EEVEE renderer
    scene.render.engine = 'BLENDER_EEVEE'
        
    bpy.ops.render.render(write_still=True)
    print(f"Rendered preview: {filepath}")

def main():
    print("=== Generating 3D KidsBook Assets for Beatrix Potter's Peter Rabbit ===")
    manifest = {}
    
    # 1. Standalone Peter Rabbit Model
    reset_scene()
    create_peter_rabbit(location=(0,0,0), scale=(1,1,1), has_coat=True, name_prefix="Peter")
    peter_path = os.path.join(MODELS_DIR, "peter_rabbit.glb")
    manifest["peter_rabbit"] = {"path": peter_path, "size_kb": export_active_scene_glb(peter_path)}
    
    # 2. Master Storybook
    build_master_book()
    book_path = os.path.join(MODELS_DIR, "storybook_master.glb")
    manifest["storybook_master"] = {"path": book_path, "size_kb": export_active_scene_glb(book_path)}
    
    # 3. Chapter 1: The Burrow
    build_scene1_burrow()
    c1_model = os.path.join(MODELS_DIR, "scene1_burrow.glb")
    manifest["scene1_burrow"] = {"path": c1_model, "size_kb": export_active_scene_glb(c1_model)}
    c1_render = os.path.join(RENDERS_DIR, "chapter1_burrow.png")
    render_preview(c1_render)
    
    # 4. Chapter 2: The Garden
    build_scene2_garden()
    c2_model = os.path.join(MODELS_DIR, "scene2_garden.glb")
    manifest["scene2_garden"] = {"path": c2_model, "size_kb": export_active_scene_glb(c2_model)}
    c2_render = os.path.join(RENDERS_DIR, "chapter2_garden.png")
    render_preview(c2_render)
    
    # 5. Chapter 3: The Adventure
    build_scene3_adventure()
    c3_model = os.path.join(MODELS_DIR, "scene3_adventure.glb")
    manifest["scene3_adventure"] = {"path": c3_model, "size_kb": export_active_scene_glb(c3_model)}
    c3_render = os.path.join(RENDERS_DIR, "chapter3_adventure.png")
    render_preview(c3_render)
    
    # 6. Chapter 4: Bedtime
    build_scene4_bedtime()
    c4_model = os.path.join(MODELS_DIR, "scene4_bedtime.glb")
    manifest["scene4_bedtime"] = {"path": c4_model, "size_kb": export_active_scene_glb(c4_model)}
    c4_render = os.path.join(RENDERS_DIR, "chapter4_bedtime.png")
    render_preview(c4_render)
    
    # Save manifest
    manifest_path = os.path.join(PROJECT_ROOT, "assets", "assets_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print("=== All 3D Assets and Renders Generated Successfully! ===")

if __name__ == "__main__":
    main()
