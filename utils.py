import bpy
from bpy.types import Material
from mathutils import Vector
from enum import Enum


def hex_to_blender_color(hex_str: str):
    hex_str = hex_str.removeprefix('#')
    srgb = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    linear = []
    for c in srgb:
        if c <= 0.04045:
            linear.append(c / 12.92)
        else:
            linear.append(((c + 0.055) / 1.055) ** 2.4)
    return (*linear, 1.0)


def get_or_create_dwpose_material(material_name: str, material_color: str) -> Material:
    material = bpy.data.materials.get(material_name)
    if not material:
        material = bpy.data.materials.new(name=material_name)
        if not material.node_tree:
            material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs['Color'].default_value = hex_to_blender_color(material_color)
        node_emission.inputs['Strength'].default_value = 1.0
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        links.new(node_emission.outputs['Emission'], node_out.inputs['Surface'])
    return material


def create_or_get_collection(name, parent_collection):
    collection = bpy.data.collections.get(name)
    if not collection:
        collection = bpy.data.collections.new(name)
        if parent_collection:
            parent_collection.children.link(collection)
    return collection


def create_or_get_markers_collection(context):
    props = context.scene.dwpose_map_props
    return create_or_get_collection(f"DWPose Markers ({props.armature.name})", context.scene.collection)


def create_or_get_mesh(name: str):
    mesh = bpy.data.meshes.get(name)
    if not mesh:
        mesh = bpy.data.meshes.new(name)
    return mesh


def create_or_get_camera(name: str):
    camera = bpy.data.cameras.get(name)
    if not camera:
        camera = bpy.data.cameras.new(name)
    return camera


def create_or_get_view_layer(name: str):
    view_layer = bpy.context.scene.view_layers.get(name)
    if not view_layer:
        view_layer = bpy.context.scene.view_layers.new(name=name)
    return view_layer


def create_or_get_object(name: str, data, collection):
    obj = bpy.data.objects.get(name)
    if not obj:
        obj = bpy.data.objects.new(name, data)
        collection.objects.link(obj)
    return obj


def get_armature_center_of_mass(armature):
    total_com = Vector((0, 0, 0))
    mesh_count = 0
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and (obj.parent == armature or any(m.type == 'ARMATURE' and m.object == armature for m in obj.modifiers))]
    if not meshes:
        return armature.matrix_world.to_translation()
    for mesh_obj in meshes:
        local_coords = [v.co for v in mesh_obj.data.vertices]
        if local_coords:
            mesh_com_local = sum(local_coords, Vector()) / len(local_coords)
            mesh_com_world = mesh_obj.matrix_world @ mesh_com_local
            total_com += mesh_com_world
            mesh_count += 1
    return total_com / mesh_count if mesh_count > 0 else armature.location


def create_or_get_point_geometry_nodes(node_group_name):
    node_group = bpy.data.node_groups.get(node_group_name)
    if not node_group:
        node_group = bpy.data.node_groups.new(name=node_group_name, type='GeometryNodeTree')
        node_group.interface.new_socket(name="Material", in_out='INPUT', socket_type='NodeSocketMaterial')
        node_group.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
        node_group.interface.new_socket(name="Mesh", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        nodes = node_group.nodes
        nodes.clear()
        links = node_group.links
        node_input = nodes.new(type='NodeGroupInput')
        node_input.location = (0, 0)
        node_output = nodes.new(type='NodeGroupOutput')
        node_output.location = (600, 0)
        node_output.is_active_output = True
        node_ico = nodes.new(type='GeometryNodeMeshIcoSphere')
        node_ico.location = (200, 0)
        node_ico.inputs['Subdivisions'].default_value = 7
        material_node = nodes.new(type='GeometryNodeSetMaterial')
        material_node.location = (400, 0)
        links.new(node_input.outputs["Material"], material_node.inputs['Material'])
        links.new(node_input.outputs["Radius"], node_ico.inputs['Radius'])
        links.new(node_ico.outputs['Mesh'], material_node.inputs['Geometry'])
        links.new(material_node.outputs['Geometry'], node_output.inputs['Mesh'])
    material_input_id = node_group.interface.items_tree.get("Material").identifier
    radius_input_id = node_group.interface.items_tree.get("Radius").identifier
    return (node_group, material_input_id, radius_input_id)


def create_or_get_line_geometry_nodes(node_group_name):
    node_group = bpy.data.node_groups.get(node_group_name)
    if not node_group:
        node_group = bpy.data.node_groups.new(name=node_group_name, type='GeometryNodeTree')
        node_group.interface.new_socket(name="From", in_out='INPUT', socket_type='NodeSocketObject')
        node_group.interface.new_socket(name="To", in_out='INPUT', socket_type='NodeSocketObject')
        node_group.interface.new_socket(name="Material", in_out='INPUT', socket_type='NodeSocketMaterial')
        node_group.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
        node_group.interface.new_socket(name="Mesh", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        nodes = node_group.nodes
        nodes.clear()
        links = node_group.links
        node_input = nodes.new(type='NodeGroupInput')
        node_input.location = (0, 0)
        node_output = nodes.new(type='NodeGroupOutput')
        node_output.location = (1000, 0)
        node_output.is_active_output = True
        node_from = nodes.new(type='GeometryNodeObjectInfo')
        node_from.location = (200, 0)
        node_from.transform_space = 'RELATIVE'
        node_to = nodes.new(type='GeometryNodeObjectInfo')
        node_to.location = (200, -250)
        node_to.transform_space = 'RELATIVE'
        node_line = nodes.new(type='GeometryNodeCurvePrimitiveLine')
        node_line.location = (400, 0)
        node_circle = nodes.new(type='GeometryNodeCurvePrimitiveCircle')
        node_circle.location = (400, -150)
        node_c2m = nodes.new(type='GeometryNodeCurveToMesh')
        node_c2m.location = (600, 0)
        node_material = nodes.new(type='GeometryNodeSetMaterial')
        node_material.location = (800, 0)
        links.new(node_input.outputs["From"], node_from.inputs['Object'])
        links.new(node_input.outputs["To"], node_to.inputs['Object'])
        links.new(node_input.outputs["Material"], node_material.inputs['Material'])
        links.new(node_input.outputs["Radius"], node_circle.inputs['Radius'])
        links.new(node_from.outputs['Location'], node_line.inputs['Start'])
        links.new(node_to.outputs['Location'], node_line.inputs['End'])
        links.new(node_line.outputs['Curve'], node_c2m.inputs['Curve'])
        links.new(node_circle.outputs['Curve'], node_c2m.inputs['Profile Curve'])
        links.new(node_c2m.outputs['Mesh'], node_material.inputs['Geometry'])
        links.new(node_material.outputs['Geometry'], node_output.inputs['Mesh'])
    from_input_id = node_group.interface.items_tree.get("From").identifier
    to_input_id = node_group.interface.items_tree.get("To").identifier
    material_input_id = node_group.interface.items_tree.get("Material").identifier
    radius_input_id = node_group.interface.items_tree.get("Radius").identifier
    return (node_group, from_input_id, to_input_id, material_input_id, radius_input_id)


class DWPoseBodyMarker(Enum):
    NOSE = ("dwpose_nose", "bone_nose", "#ff0000")
    EYE_L = ("dwpose_eye_l", "bone_eye_l", "#ff00ff")
    EAR_L = ("dwpose_ear_l", "bone_ear_l", "#ff0055")
    EYE_R = ("dwpose_eye_r", "bone_eye_r", "#aa00ff")
    EAR_R = ("dwpose_ear_r", "bone_ear_r", "#ff00aa")
    NECK = ("dwpose_neck", "bone_neck", "#ff5500")
    SHOULDER_L = ("dwpose_shoulder_l", "bone_shoulder_l", "#55ff00")
    ELBOW_L = ("dwpose_elbow_l", "bone_elbow_l", "#00ff00")
    WRIST_L = ("dwpose_wrist_l", "bone_wrist_l", "#00ff55")
    SHOULDER_R = ("dwpose_shoulder_r", "bone_shoulder_r", "#ffaa00")
    ELBOW_R = ("dwpose_elbow_r", "bone_elbow_r", "#ffff00")
    WRIST_R = ("dwpose_wrist_r", "bone_wrist_r", "#aaff00")
    THIGH_L = ("dwpose_thigh_l", "bone_thigh_l", "#0055ff")
    KNEE_L = ("dwpose_knee_l", "bone_knee_l", "#0000ff")
    FOOT_L = ("dwpose_foot_l", "bone_foot_l", "#5500ff")
    TOE_L = ("dwpose_toe_l", "bone_toe_l", "#5555ff")
    HEEL_L = ("dwpose_heel_l", "bone_heel_l", "#5555ff")
    THIGH_R = ("dwpose_thigh_r", "bone_thigh_r", "#00ffaa")
    KNEE_R = ("dwpose_knee_r", "bone_knee_r", "#00ffff")
    FOOT_R = ("dwpose_foot_r", "bone_foot_r", "#00aaff")
    TOE_R = ("dwpose_toe_r", "bone_toe_r", "#55aaff")
    HEEL_R = ("dwpose_heel_r", "bone_heel_r", "#55aaff")


    def __init__(self, id: str, bone: str, color: str):
        self.id = id
        self.bone = bone
        self.color = color


class DWPoseBodyLine(Enum):
    NOSE_TO_EYE_L = (DWPoseBodyMarker.NOSE, DWPoseBodyMarker.EYE_L, "#990099")
    NOSE_TO_EYE_R = (DWPoseBodyMarker.NOSE, DWPoseBodyMarker.EYE_R, "#330099")
    EYE_L_TO_EAR_L = (DWPoseBodyMarker.EYE_L, DWPoseBodyMarker.EAR_L, "#990066")
    EYE_R_TO_EAR_R = (DWPoseBodyMarker.EYE_R, DWPoseBodyMarker.EAR_R, "#660099")
    NECK_TO_NOSE = (DWPoseBodyMarker.NECK, DWPoseBodyMarker.NOSE, "#000099")
    NECK_TO_SHOULDER_L = (DWPoseBodyMarker.NECK, DWPoseBodyMarker.SHOULDER_L, "#993300")
    NECK_TO_SHOULDER_R = (DWPoseBodyMarker.NECK, DWPoseBodyMarker.SHOULDER_R, "#990000")
    NECK_TO_THIGH_L = (DWPoseBodyMarker.NECK, DWPoseBodyMarker.THIGH_L, "#009999")
    NECK_TO_THIGH_R = (DWPoseBodyMarker.NECK, DWPoseBodyMarker.THIGH_R, "#009900")
    SHOULDER_L_TO_ELBOW_L = (DWPoseBodyMarker.SHOULDER_L, DWPoseBodyMarker.ELBOW_L, "#669900")
    SHOULDER_R_TO_ELBOW_R = (DWPoseBodyMarker.SHOULDER_R, DWPoseBodyMarker.ELBOW_R, "#996600")
    ELBOW_L_TO_WRIST_L = (DWPoseBodyMarker.ELBOW_L, DWPoseBodyMarker.WRIST_L, "#339900")
    ELBOW_R_TO_WRIST_R = (DWPoseBodyMarker.ELBOW_R, DWPoseBodyMarker.WRIST_R, "#999900")
    THIGH_L_TO_KNEE_L = (DWPoseBodyMarker.THIGH_L, DWPoseBodyMarker.KNEE_L, "#006699")
    THIGH_R_TO_KNEE_R = (DWPoseBodyMarker.THIGH_R, DWPoseBodyMarker.KNEE_R, "#009933")
    KNEE_L_TO_FOOT_L = (DWPoseBodyMarker.KNEE_L, DWPoseBodyMarker.FOOT_L, "#003399")
    KNEE_R_TO_FOOT_R = (DWPoseBodyMarker.KNEE_R, DWPoseBodyMarker.FOOT_R, "#009966")
    FOOT_L_TO_TOE_L = (DWPoseBodyMarker.FOOT_L, DWPoseBodyMarker.TOE_L, "#333399")
    FOOT_L_TO_HEEL_L = (DWPoseBodyMarker.FOOT_L, DWPoseBodyMarker.HEEL_L, "#333399")
    FOOT_R_TO_TOE_R = (DWPoseBodyMarker.FOOT_R, DWPoseBodyMarker.TOE_R, "#00cc99")
    FOOT_R_TO_HEEL_R = (DWPoseBodyMarker.FOOT_R, DWPoseBodyMarker.HEEL_R, "#00cc99")


    def __init__(self, from_marker: DWPoseBodyMarker, to_marker: DWPoseBodyMarker, color: str):
        self.from_marker = from_marker
        self.to_marker = to_marker
        self.color = color


class DWPoseHandMarker(Enum):
    HAND_L = ("dwpose_hand_l", "bone_hand_l", "#0000ff")
    HAND_L_THUMB1 = ("dwpose_hand_l_thumb1", "bone_hand_l_thumb1", "#0000ff")
    HAND_L_THUMB2 = ("dwpose_hand_l_thumb2", "bone_hand_l_thumb2", "#0000ff")
    HAND_L_THUMB3 = ("dwpose_hand_l_thumb3", "bone_hand_l_thumb3", "#0000ff")
    HAND_L_THUMB4 = ("dwpose_hand_l_thumb4", "bone_hand_l_thumb4", "#0000ff")
    HAND_L_INDEX1 = ("dwpose_hand_l_index1", "bone_hand_l_index1", "#0000ff")
    HAND_L_INDEX2 = ("dwpose_hand_l_index2", "bone_hand_l_index2", "#0000ff")
    HAND_L_INDEX3 = ("dwpose_hand_l_index3", "bone_hand_l_index3", "#0000ff")
    HAND_L_INDEX4 = ("dwpose_hand_l_index4", "bone_hand_l_index4", "#0000ff")
    HAND_L_MIDDLE1 = ("dwpose_hand_l_middle1", "bone_hand_l_middle1", "#0000ff")
    HAND_L_MIDDLE2 = ("dwpose_hand_l_middle2", "bone_hand_l_middle2", "#0000ff")
    HAND_L_MIDDLE3 = ("dwpose_hand_l_middle3", "bone_hand_l_middle3", "#0000ff")
    HAND_L_MIDDLE4 = ("dwpose_hand_l_middle4", "bone_hand_l_middle4", "#0000ff")
    HAND_L_RING1 = ("dwpose_hand_l_ring1", "bone_hand_l_ring1", "#0000ff")
    HAND_L_RING2 = ("dwpose_hand_l_ring2", "bone_hand_l_ring2", "#0000ff")
    HAND_L_RING3 = ("dwpose_hand_l_ring3", "bone_hand_l_ring3", "#0000ff")
    HAND_L_RING4 = ("dwpose_hand_l_ring4", "bone_hand_l_ring4", "#0000ff")
    HAND_L_PINKY1 = ("dwpose_hand_l_pinky1", "bone_hand_l_pinky1", "#0000ff")
    HAND_L_PINKY2 = ("dwpose_hand_l_pinky2", "bone_hand_l_pinky2", "#0000ff")
    HAND_L_PINKY3 = ("dwpose_hand_l_pinky3", "bone_hand_l_pinky3", "#0000ff")
    HAND_L_PINKY4 = ("dwpose_hand_l_pinky4", "bone_hand_l_pinky4", "#0000ff")
    HAND_R = ("dwpose_hand_r", "bone_hand_r", "#0000ff")
    HAND_R_THUMB1 = ("dwpose_hand_r_thumb1", "bone_hand_r_thumb1", "#0000ff")
    HAND_R_THUMB2 = ("dwpose_hand_r_thumb2", "bone_hand_r_thumb2", "#0000ff")
    HAND_R_THUMB3 = ("dwpose_hand_r_thumb3", "bone_hand_r_thumb3", "#0000ff")
    HAND_R_THUMB4 = ("dwpose_hand_r_thumb4", "bone_hand_r_thumb4", "#0000ff")
    HAND_R_INDEX1 = ("dwpose_hand_r_index1", "bone_hand_r_index1", "#0000ff")
    HAND_R_INDEX2 = ("dwpose_hand_r_index2", "bone_hand_r_index2", "#0000ff")
    HAND_R_INDEX3 = ("dwpose_hand_r_index3", "bone_hand_r_index3", "#0000ff")
    HAND_R_INDEX4 = ("dwpose_hand_r_index4", "bone_hand_r_index4", "#0000ff")
    HAND_R_MIDDLE1 = ("dwpose_hand_r_middle1", "bone_hand_r_middle1", "#0000ff")
    HAND_R_MIDDLE2 = ("dwpose_hand_r_middle2", "bone_hand_r_middle2", "#0000ff")
    HAND_R_MIDDLE3 = ("dwpose_hand_r_middle3", "bone_hand_r_middle3", "#0000ff")
    HAND_R_MIDDLE4 = ("dwpose_hand_r_middle4", "bone_hand_r_middle4", "#0000ff")
    HAND_R_RING1 = ("dwpose_hand_r_ring1", "bone_hand_r_ring1", "#0000ff")
    HAND_R_RING2 = ("dwpose_hand_r_ring2", "bone_hand_r_ring2", "#0000ff")
    HAND_R_RING3 = ("dwpose_hand_r_ring3", "bone_hand_r_ring3", "#0000ff")
    HAND_R_RING4 = ("dwpose_hand_r_ring4", "bone_hand_r_ring4", "#0000ff")
    HAND_R_PINKY1 = ("dwpose_hand_r_pinky1", "bone_hand_r_pinky1", "#0000ff")
    HAND_R_PINKY2 = ("dwpose_hand_r_pinky2", "bone_hand_r_pinky2", "#0000ff")
    HAND_R_PINKY3 = ("dwpose_hand_r_pinky3", "bone_hand_r_pinky3", "#0000ff")
    HAND_R_PINKY4 = ("dwpose_hand_r_pinky4", "bone_hand_r_pinky4", "#0000ff")


    def __init__(self, id: str, bone: str, color: str):
        self.id = id
        self.bone = bone
        self.color = color


class DWPoseHandLine(Enum):
    HAND_L_TO_HAND_L_THUMB1 = (DWPoseHandMarker.HAND_L, DWPoseHandMarker.HAND_L_THUMB1, "#ff0000")
    HAND_L_TO_HAND_L_INDEX1 = (DWPoseHandMarker.HAND_L, DWPoseHandMarker.HAND_L_INDEX1, "#ccff00")
    HAND_L_TO_HAND_L_MIDDLE1 = (DWPoseHandMarker.HAND_L, DWPoseHandMarker.HAND_L_MIDDLE1, "#00ff66")
    HAND_L_TO_HAND_L_RING1 = (DWPoseHandMarker.HAND_L, DWPoseHandMarker.HAND_L_RING1, "#0066ff")
    HAND_L_TO_HAND_L_PINKY1 = (DWPoseHandMarker.HAND_L, DWPoseHandMarker.HAND_L_PINKY1, "#cc00ff")
    HAND_L_THUMB1_TO_HAND_L_THUMB2 = (DWPoseHandMarker.HAND_L_THUMB1, DWPoseHandMarker.HAND_L_THUMB2, "#ff4d00")
    HAND_L_THUMB2_TO_HAND_L_THUMB3 = (DWPoseHandMarker.HAND_L_THUMB2, DWPoseHandMarker.HAND_L_THUMB3, "#ff9900")
    HAND_L_THUMB3_TO_HAND_L_THUMB4 = (DWPoseHandMarker.HAND_L_THUMB3, DWPoseHandMarker.HAND_L_THUMB4, "#ffff00")
    HAND_L_INDEX1_TO_HAND_L_INDEX2 = (DWPoseHandMarker.HAND_L_INDEX1, DWPoseHandMarker.HAND_L_INDEX2, "#80ff00")
    HAND_L_INDEX2_TO_HAND_L_INDEX3 = (DWPoseHandMarker.HAND_L_INDEX2, DWPoseHandMarker.HAND_L_INDEX3, "#33ff00")
    HAND_L_INDEX3_TO_HAND_L_INDEX4 = (DWPoseHandMarker.HAND_L_INDEX3, DWPoseHandMarker.HAND_L_INDEX4, "#00ff19")
    HAND_L_MIDDLE1_TO_HAND_L_MIDDLE2 = (DWPoseHandMarker.HAND_L_MIDDLE1, DWPoseHandMarker.HAND_L_MIDDLE2, "#00ffb3")
    HAND_L_MIDDLE2_TO_HAND_L_MIDDLE3 = (DWPoseHandMarker.HAND_L_MIDDLE2, DWPoseHandMarker.HAND_L_MIDDLE3, "#00ffff")
    HAND_L_MIDDLE3_TO_HAND_L_MIDDLE4 = (DWPoseHandMarker.HAND_L_MIDDLE3, DWPoseHandMarker.HAND_L_MIDDLE4, "#00b4ff")
    HAND_L_RING1_TO_HAND_L_RING2 = (DWPoseHandMarker.HAND_L_RING1, DWPoseHandMarker.HAND_L_RING2, "#0019ff")
    HAND_L_RING2_TO_HAND_L_RING3 = (DWPoseHandMarker.HAND_L_RING2, DWPoseHandMarker.HAND_L_RING3, "#3300ff")
    HAND_L_RING3_TO_HAND_L_RING4 = (DWPoseHandMarker.HAND_L_RING3, DWPoseHandMarker.HAND_L_RING4, "#8000ff")
    HAND_L_PINKY1_TO_HAND_L_PINKY2 = (DWPoseHandMarker.HAND_L_PINKY1, DWPoseHandMarker.HAND_L_PINKY2, "#ff00e6")
    HAND_L_PINKY2_TO_HAND_L_PINKY3 = (DWPoseHandMarker.HAND_L_PINKY2, DWPoseHandMarker.HAND_L_PINKY3, "#ff009a")
    HAND_L_PINKY3_TO_HAND_L_PINKY4 = (DWPoseHandMarker.HAND_L_PINKY3, DWPoseHandMarker.HAND_L_PINKY4, "#fb004c")
    HAND_R_TO_HAND_R_THUMB1 = (DWPoseHandMarker.HAND_R, DWPoseHandMarker.HAND_R_THUMB1, "#ff0000")
    HAND_R_TO_HAND_R_INDEX1 = (DWPoseHandMarker.HAND_R, DWPoseHandMarker.HAND_R_INDEX1, "#ccff00")
    HAND_R_TO_HAND_R_MIDDLE1 = (DWPoseHandMarker.HAND_R, DWPoseHandMarker.HAND_R_MIDDLE1, "#00ff66")
    HAND_R_TO_HAND_R_RING1 = (DWPoseHandMarker.HAND_R, DWPoseHandMarker.HAND_R_RING1, "#0066ff")
    HAND_R_TO_HAND_R_PINKY1 = (DWPoseHandMarker.HAND_R, DWPoseHandMarker.HAND_R_PINKY1, "#cc00ff")
    HAND_R_THUMB1_TO_HAND_R_THUMB2 = (DWPoseHandMarker.HAND_R_THUMB1, DWPoseHandMarker.HAND_R_THUMB2, "#ff4d00")
    HAND_R_THUMB2_TO_HAND_R_THUMB3 = (DWPoseHandMarker.HAND_R_THUMB2, DWPoseHandMarker.HAND_R_THUMB3, "#ff9900")
    HAND_R_THUMB3_TO_HAND_R_THUMB4 = (DWPoseHandMarker.HAND_R_THUMB3, DWPoseHandMarker.HAND_R_THUMB4, "#ffff00")
    HAND_R_INDEX1_TO_HAND_R_INDEX2 = (DWPoseHandMarker.HAND_R_INDEX1, DWPoseHandMarker.HAND_R_INDEX2, "#80ff00")
    HAND_R_INDEX2_TO_HAND_R_INDEX3 = (DWPoseHandMarker.HAND_R_INDEX2, DWPoseHandMarker.HAND_R_INDEX3, "#33ff00")
    HAND_R_INDEX3_TO_HAND_R_INDEX4 = (DWPoseHandMarker.HAND_R_INDEX3, DWPoseHandMarker.HAND_R_INDEX4, "#00ff19")
    HAND_R_MIDDLE1_TO_HAND_R_MIDDLE2 = (DWPoseHandMarker.HAND_R_MIDDLE1, DWPoseHandMarker.HAND_R_MIDDLE2, "#00ffb3")
    HAND_R_MIDDLE2_TO_HAND_R_MIDDLE3 = (DWPoseHandMarker.HAND_R_MIDDLE2, DWPoseHandMarker.HAND_R_MIDDLE3, "#00ffff")
    HAND_R_MIDDLE3_TO_HAND_R_MIDDLE4 = (DWPoseHandMarker.HAND_R_MIDDLE3, DWPoseHandMarker.HAND_R_MIDDLE4, "#00b4ff")
    HAND_R_RING1_TO_HAND_R_RING2 = (DWPoseHandMarker.HAND_R_RING1, DWPoseHandMarker.HAND_R_RING2, "#0019ff")
    HAND_R_RING2_TO_HAND_R_RING3 = (DWPoseHandMarker.HAND_R_RING2, DWPoseHandMarker.HAND_R_RING3, "#3300ff")
    HAND_R_RING3_TO_HAND_R_RING4 = (DWPoseHandMarker.HAND_R_RING3, DWPoseHandMarker.HAND_R_RING4, "#8000ff")
    HAND_R_PINKY1_TO_HAND_R_PINKY2 = (DWPoseHandMarker.HAND_R_PINKY1, DWPoseHandMarker.HAND_R_PINKY2, "#ff00e6")
    HAND_R_PINKY2_TO_HAND_R_PINKY3 = (DWPoseHandMarker.HAND_R_PINKY2, DWPoseHandMarker.HAND_R_PINKY3, "#ff009a")
    HAND_R_PINKY3_TO_HAND_R_PINKY4 = (DWPoseHandMarker.HAND_R_PINKY3, DWPoseHandMarker.HAND_R_PINKY4, "#fb004c")


    def __init__(self, from_marker: DWPoseHandMarker, to_marker: DWPoseHandMarker, color: str):
        self.from_marker = from_marker
        self.to_marker = to_marker
        self.color = color
