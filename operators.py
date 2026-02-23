import math
from bpy.types import Operator, Object
from mathutils import Vector
from . import utils


class DWPOSE_SCENE_OT_setup_scene_for_dwpose_render(Operator):
    bl_idname = "object.setup_scene_for_dwpose_render"
    bl_label = "Setup scene"
    bl_description = "Setup scene for DWPose render."
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        self._setup_view_settings(context.scene.view_settings)
        self._setup_world_background(context.scene.world)
        self._setup_camera(context)
        self._setup_view_layer(context)
        self.report({'INFO'}, "The scene has been successfully set up.")
        return {'FINISHED'}


    def _setup_view_settings(self, view_settings):
        view_settings.view_transform = 'Standard'
        view_settings.look = 'None'
        view_settings.exposure = 0.0
        view_settings.gamma = 1.0
    
    
    def _setup_world_background(sefl, world):
        if world:
            node_tree = world.node_tree
            if node_tree:
                node_background = next((n for n in node_tree.nodes if n.type == 'BACKGROUND'), None)
                if node_background:
                    node_background.inputs['Color'].default_value = (0, 0, 0, 1)
                    node_background.inputs['Strength'].default_value = 1.0


    def _setup_camera(sefl, context):
        props = context.scene.dwpose_map_props
        armature = props.armature
        if armature:
            markers_collection = utils.create_or_get_markers_collection(context)
            camera_collection = utils.create_or_get_collection(f"DWPose Camera ({props.armature.name})", markers_collection)
            camera_parent_empty = utils.create_or_get_object(f"camera_parent_marker_{armature.name}", None, camera_collection)
            camera_parent_empty.empty_display_type = 'PLAIN_AXES'
            camera_parent_empty.empty_display_size = 1.0
            camera_parent_empty.location = utils.get_armature_center_of_mass(armature)
            camera = utils.create_or_get_camera("DWPoseCamera")
            camera_obj = utils.create_or_get_object(f"DWPoseCamera_{armature.name}", camera, camera_collection)
            camera_obj.data.type = 'ORTHO'
            camera_obj.data.ortho_scale = 5.0
            camera_obj.parent = camera_parent_empty
            camera_obj.location = (-5.0, 0, 0.0)
            camera_obj.rotation_euler = (math.radians(90), math.radians(0), math.radians(-90))
            context.scene.camera = camera_obj
    
    
    def _setup_view_layer(self, context):
        props = context.scene.dwpose_map_props
        armature = props.armature
        if armature:
            markers_collection = utils.create_or_get_markers_collection(context)
            view_layer = utils.create_or_get_view_layer(f"DWPoseViewLayer_{armature.name}")
            for lc in view_layer.layer_collection.children:
                if lc.name == markers_collection.name:
                    lc.exclude = False
                else:
                    lc.exclude = True
                    lc.collection.hide_render = True
            context.window.view_layer = view_layer


class DWPOSE_BONES_OT_create_dwpose(Operator):
    bl_idname = "object.create_dwpose"
    bl_label = "Create DWPose"
    bl_description = "Create meshes to display DWPose."
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        props = context.scene.dwpose_map_props
        return props.armature and (props.body_enable or props.hands_enable or props.face_enable)


    def execute(self, context):
        props = context.scene.dwpose_map_props
        markers_collection = utils.create_or_get_markers_collection(context)
        point_mesh = utils.create_or_get_mesh("DWPosePoint")
        line_mesh = utils.create_or_get_mesh("DWPoseLine")
        if props.body_enable:
            body_markers_collection = utils.create_or_get_collection(f"DWPose Body ({props.armature.name})", markers_collection)
            body_markers = self._create_body_markers(props, body_markers_collection)
            self._create_body_points(props.armature, body_markers, point_mesh, body_markers_collection, props.body_points_radius)
            self._create_body_lines(props.armature, body_markers, line_mesh, body_markers_collection, props.body_lines_radius)
        if props.hands_enable:
            hands_markers_collection = utils.create_or_get_collection(f"DWPose Hands ({props.armature.name})", markers_collection)
            hands_markers = self._create_hands_markers(props, hands_markers_collection)
            self._create_hands_points(props.armature, hands_markers, point_mesh, hands_markers_collection, props.hands_points_radius)
            self._create_hands_lines(props.armature, hands_markers, line_mesh, hands_markers_collection, props.hands_lines_radius)
        if props.face_enable:
            face_markers_collection = utils.create_or_get_collection(f"DWPose Face ({props.armature.name})", markers_collection)
        self.report({'INFO'}, "The DWPose was successfully created.")
        return {'FINISHED'}


    def _create_body_markers(self, props, collection) -> dict[utils.DWPoseBodyMarker, Object]:
        markers: dict[utils.DWPoseBodyMarker, Object] = {}
        for marker in utils.DWPoseBodyMarker:
            bone = getattr(props, marker.bone, None)
            if not bone:
                if (marker.id == "dwpose_nose" or marker.id == "dwpose_eye_l" or marker.id == "dwpose_ear_l" or \
                    marker.id == "dwpose_eye_r" or marker.id == "dwpose_ear_r"):
                    bone = props.bone_head
                elif marker.id == "dwpose_heel_l" and props.bone_toe_l:
                    bone = props.bone_foot_l
                elif marker.id == "dwpose_heel_r" and props.bone_toe_r:
                    bone = props.bone_foot_r
            marker_empty = self._create_marker(props, marker.id, collection, bone, 0.3)
            if not marker_empty:
                continue
            if bone == props.bone_head:
                if marker.id == "dwpose_nose":
                    marker_empty.location += Vector((0.0, 0.07, 0.15)) * marker_empty.scale
                elif marker.id == "dwpose_eye_l":
                    marker_empty.location += Vector((-0.039833, 0.106656, 0.10943)) * marker_empty.scale
                elif marker.id == "dwpose_eye_r":
                    marker_empty.location += Vector((0.039833, 0.106656, 0.10943)) * marker_empty.scale
                elif marker.id == "dwpose_ear_l":
                    marker_empty.location += Vector((0.095, 0.082615, 0.025)) * marker_empty.scale
                elif marker.id == "dwpose_ear_r":
                    marker_empty.location += Vector((-0.095, 0.082615, 0.025)) * marker_empty.scale
            elif bone == props.bone_foot_l:
                if marker.id == "dwpose_heel_l":
                    marker_empty.location += Vector((0.0, 0.0, -0.129)) * marker_empty.scale
            elif bone == props.bone_foot_r:
                if marker.id == "dwpose_heel_r":
                    marker_empty.location += Vector((0.0, 0.0, -0.129)) * marker_empty.scale
            markers[marker] = marker_empty
        return markers
    
    
    def _create_hands_markers(self, props, collection) -> dict[utils.DWPoseHandMarker, Object]:
        markers: dict[utils.DWPoseHandMarker, Object] = {}
        for marker in utils.DWPoseHandMarker:
            bone = getattr(props, marker.bone, None)
            marker_empty = self._create_marker(props, marker.id, collection, bone, 0.1)
            if not marker_empty:
                continue
            if marker.id == "dwpose_hand_l":
                marker_empty.location += Vector((0.0, 0.03, 0.0)) * marker_empty.scale
            if marker.id == "dwpose_hand_r":
                marker_empty.location += Vector((0.0, 0.03, 0.0)) * marker_empty.scale
            markers[marker] = marker_empty
        return markers


    def _create_marker(self, props, marker_id: str, collection, bone, size) -> Object:
        if not bone:
            return None
        armature = props.armature
        bone_pose = armature.pose.bones.get(bone)
        if not bone_pose:
            return None
        marker_empty = utils.create_or_get_object(f"{marker_id}_marker_{armature.name}", None, collection)
        marker_empty.empty_display_type = 'PLAIN_AXES'
        marker_empty.empty_display_size = size
        world_matrix = (armature.matrix_world @ bone_pose.matrix).copy()
        for i in range(3):
            world_matrix[i].normalize()
        marker_empty.matrix_world = world_matrix
        marker_empty.parent = armature
        marker_empty.parent_type = 'BONE'
        marker_empty.parent_bone = bone
        marker_empty.matrix_world = world_matrix
        return marker_empty


    def _create_body_points(self, armature, markers: dict[utils.DWPoseBodyMarker, Object], mesh, collection, radius):
        for marker, obj in markers.items():
            point = utils.create_or_get_object(f"{marker.id}_point_{armature.name}", mesh, collection)
            point.matrix_world = obj.matrix_world
            point.parent = obj
            point.matrix_world = obj.matrix_world
            material = utils.get_or_create_dwpose_material(f"{marker.id}_point_material", marker.color)
            if material.name not in point.data.materials:
                point.data.materials.append(material)
            node_group, material_input, radius_input = utils.create_or_get_point_geometry_nodes("DWPosePointNodes")
            modifier = point.modifiers.new(name="DWPosePoint", type='NODES')
            modifier.node_group = node_group
            modifier[material_input] = material
            modifier[radius_input] = radius


    def _create_body_lines(self, armature, markers: dict[utils.DWPoseBodyMarker, Object], mesh, collection, radius):
        for line in utils.DWPoseBodyLine:
            from_marker = markers.get(line.from_marker)
            to_marker = markers.get(line.to_marker)
            if from_marker and to_marker:
                line_obj = utils.create_or_get_object(f"{line.from_marker.id}_to_{line.to_marker.id}_line_{armature.name}", mesh, collection)
                line_obj.matrix_world = from_marker.matrix_world
                line_obj.parent = from_marker
                line_obj.matrix_world = from_marker.matrix_world
                material = utils.get_or_create_dwpose_material(f"{line.from_marker.id}_to_{line.to_marker.id}_line_material", line.color)
                if material.name not in line_obj.data.materials:
                    line_obj.data.materials.append(material)
                node_group, from_input, to_input, material_input, radius_input = utils.create_or_get_line_geometry_nodes("DWPoseLineNodes")
                modifier = line_obj.modifiers.new(name="DWPoseLine", type='NODES')
                modifier.node_group = node_group
                modifier[from_input] = from_marker
                modifier[to_input] = to_marker
                modifier[material_input] = material
                modifier[radius_input] = radius
    
    
    def _create_hands_points(self, armature, markers: dict[utils.DWPoseHandMarker, Object], mesh, collection, radius):
        for marker, obj in markers.items():
            point = utils.create_or_get_object(f"{marker.id}_point_{armature.name}", mesh, collection)
            point.matrix_world = obj.matrix_world
            point.parent = obj
            point.matrix_world = obj.matrix_world
            material = utils.get_or_create_dwpose_material(f"{marker.id}_point_material", marker.color)
            if material.name not in point.data.materials:
                point.data.materials.append(material)
            node_group, material_input, radius_input = utils.create_or_get_point_geometry_nodes("DWPosePointNodes")
            modifier = point.modifiers.new(name="DWPosePoint", type='NODES')
            modifier.node_group = node_group
            modifier[material_input] = material
            modifier[radius_input] = radius


    def _create_hands_lines(self, armature, markers: dict[utils.DWPoseHandMarker, Object], mesh, collection, radius):
        for line in utils.DWPoseHandLine:
            from_marker = markers.get(line.from_marker)
            to_marker = markers.get(line.to_marker)
            if from_marker and to_marker:
                line_obj = utils.create_or_get_object(f"{line.from_marker.id}_to_{line.to_marker.id}_line_{armature.name}", mesh, collection)
                line_obj.matrix_world = from_marker.matrix_world
                line_obj.parent = from_marker
                line_obj.matrix_world = from_marker.matrix_world
                material = utils.get_or_create_dwpose_material(f"{line.from_marker.id}_to_{line.to_marker.id}_line_material", line.color)
                if material.name not in line_obj.data.materials:
                    line_obj.data.materials.append(material)
                node_group, from_input, to_input, material_input, radius_input = utils.create_or_get_line_geometry_nodes("DWPoseLineNodes")
                modifier = line_obj.modifiers.new(name="DWPoseLine", type='NODES')
                modifier.node_group = node_group
                modifier[from_input] = from_marker
                modifier[to_input] = to_marker
                modifier[material_input] = material
                modifier[radius_input] = radius


class DWPOSE_BONE_OT_auto_setup_bones(Operator):
    bl_idname = "object.auto_setup_bones"
    bl_label = "Auto Setup"
    bl_description = "Automatically find and place bones into fields."
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        props = context.scene.dwpose_map_props
        armature = props.armature
        if not armature:
            self.report({'WARNING'}, "Failed to set up bones: armature not selected.")
            return {'CANCELLED'}
        self._setup_bones(props, armature)
        self.report({'INFO'}, "The bones were successfully set up.")
        return {'FINISHED'}
    
    
    def _setup_bones(self, props, armature):
        props.bone_head = self._find_bone_name(armature, "head")
        props.bone_nose = self._find_bone_name(armature, "nose")
        props.bone_neck = self._find_bone_name(armature, "neck")
        props.bone_eye_l = self._find_bone_name(armature, "eye", side="l")
        props.bone_eye_r = self._find_bone_name(armature, "eye", side="r")
        props.bone_ear_l = self._find_bone_name(armature, "ear", side="l")
        props.bone_ear_r = self._find_bone_name(armature, "ear", side="r")
        props.bone_shoulder_l = self._find_bone_name(armature, "shoulder", mixamo_word="arm", side="l")
        props.bone_shoulder_r = self._find_bone_name(armature, "shoulder", mixamo_word="arm", side="r")
        props.bone_elbow_l = self._find_bone_name(armature, "elbow", mixamo_word="fore_arm", side="l")
        props.bone_elbow_r = self._find_bone_name(armature, "elbow", mixamo_word="fore_arm", side="r")
        props.bone_wrist_l = self._find_bone_name(armature, "wrist", mixamo_word="hand", side="l")
        props.bone_wrist_r = self._find_bone_name(armature, "wrist", mixamo_word="hand", side="r")
        props.bone_thigh_l = self._find_bone_name(armature, "thigh", mixamo_word="up_leg", side="l")
        props.bone_thigh_r = self._find_bone_name(armature, "thigh", mixamo_word="up_leg", side="r")
        props.bone_knee_l = self._find_bone_name(armature, "knee", mixamo_word="leg", mixamo_neg="up_leg", side="l")
        props.bone_knee_r = self._find_bone_name(armature, "knee", mixamo_word="leg", mixamo_neg="up_leg", side="r")
        props.bone_foot_l = self._find_bone_name(armature, "foot", side="l")
        props.bone_foot_r = self._find_bone_name(armature, "foot", side="r")
        props.bone_toe_l = self._find_bone_name(armature, "toe", side="l")
        props.bone_toe_r = self._find_bone_name(armature, "toe", side="r")
        props.bone_heel_l = self._find_bone_name(armature, "heel", side="l")
        props.bone_heel_r = self._find_bone_name(armature, "heel", side="r")
        props.bone_hand_l = self._find_bone_name(armature, "hand", side="l")
        props.bone_hand_r = self._find_bone_name(armature, "hand", side="r")
        props.bone_hand_l_thumb1 = self._find_bone_name(armature, "thumb1", side="l")
        props.bone_hand_r_thumb1 = self._find_bone_name(armature, "thumb1", side="r")
        props.bone_hand_l_thumb2 = self._find_bone_name(armature, "thumb2", side="l")
        props.bone_hand_r_thumb2 = self._find_bone_name(armature, "thumb2", side="r")
        props.bone_hand_l_thumb3 = self._find_bone_name(armature, "thumb3", side="l")
        props.bone_hand_r_thumb3 = self._find_bone_name(armature, "thumb3", side="r")
        props.bone_hand_l_thumb4 = self._find_bone_name(armature, "thumb4", side="l")
        props.bone_hand_r_thumb4 = self._find_bone_name(armature, "thumb4", side="r")
        props.bone_hand_l_index1 = self._find_bone_name(armature, "index1", side="l")
        props.bone_hand_r_index1 = self._find_bone_name(armature, "index1", side="r")
        props.bone_hand_l_index2 = self._find_bone_name(armature, "index2", side="l")
        props.bone_hand_r_index2 = self._find_bone_name(armature, "index2", side="r")
        props.bone_hand_l_index3 = self._find_bone_name(armature, "index3", side="l")
        props.bone_hand_r_index3 = self._find_bone_name(armature, "index3", side="r")
        props.bone_hand_l_index4 = self._find_bone_name(armature, "index4", side="l")
        props.bone_hand_r_index4 = self._find_bone_name(armature, "index4", side="r")
        props.bone_hand_l_middle1 = self._find_bone_name(armature, "middle1", side="l")
        props.bone_hand_r_middle1 = self._find_bone_name(armature, "middle1", side="r")
        props.bone_hand_l_middle2 = self._find_bone_name(armature, "middle2", side="l")
        props.bone_hand_r_middle2 = self._find_bone_name(armature, "middle2", side="r")
        props.bone_hand_l_middle3 = self._find_bone_name(armature, "middle3", side="l")
        props.bone_hand_r_middle3 = self._find_bone_name(armature, "middle3", side="r")
        props.bone_hand_l_middle4 = self._find_bone_name(armature, "middle4", side="l")
        props.bone_hand_r_middle4 = self._find_bone_name(armature, "middle4", side="r")
        props.bone_hand_l_ring1 = self._find_bone_name(armature, "ring1", side="l")
        props.bone_hand_r_ring1 = self._find_bone_name(armature, "ring1", side="r")
        props.bone_hand_l_ring2 = self._find_bone_name(armature, "ring2", side="l")
        props.bone_hand_r_ring2 = self._find_bone_name(armature, "ring2", side="r")
        props.bone_hand_l_ring3 = self._find_bone_name(armature, "ring3", side="l")
        props.bone_hand_r_ring3 = self._find_bone_name(armature, "ring3", side="r")
        props.bone_hand_l_ring4 = self._find_bone_name(armature, "ring4", side="l")
        props.bone_hand_r_ring4 = self._find_bone_name(armature, "ring4", side="r")
        props.bone_hand_l_pinky1 = self._find_bone_name(armature, "pinky1", side="l")
        props.bone_hand_r_pinky1 = self._find_bone_name(armature, "pinky1", side="r")
        props.bone_hand_l_pinky2 = self._find_bone_name(armature, "pinky2", side="l")
        props.bone_hand_r_pinky2 = self._find_bone_name(armature, "pinky2", side="r")
        props.bone_hand_l_pinky3 = self._find_bone_name(armature, "pinky3", side="l")
        props.bone_hand_r_pinky3 = self._find_bone_name(armature, "pinky3", side="r")
        props.bone_hand_l_pinky4 = self._find_bone_name(armature, "pinky4", side="l")
        props.bone_hand_r_pinky4 = self._find_bone_name(armature, "pinky4", side="r")

    
    def _find_bone_name(self, armature, word: str, mixamo_word: str = "", mixamo_neg: str = "", side: str = "") -> str:
        result = ""
        for bone in armature.data.bones:
            bone_name = bone.name
            bone_name_clear = self._clear_bone_name_lower(bone_name)
            target_word = word.lower()
            if "mixamo" in bone_name_clear:
                bone_name_clear = bone_name_clear.replace("mixamorig", "").replace("mixamo", "")
                if mixamo_word:
                    target_word = mixamo_word.lower()
            if target_word in bone_name_clear and (not mixamo_neg or mixamo_neg not in bone_name_clear):
                bone_name_clear = bone_name_clear.replace(target_word, "")
                if side:
                    target_side = side.lower()
                    if target_side.startswith("l"):
                        target_side_full = "_left"
                    else:
                        target_side_full = "_right"
                    target_side = "_" + target_side
                    bone_name_clear = bone_name_clear.replace(".l", "_l").replace(".r", "_r")
                    if (target_side + "_" in bone_name_clear or bone_name_clear.endswith(target_side)) or \
                        (target_side_full + "_" in bone_name_clear or bone_name_clear.endswith(target_side_full)):
                        result = bone_name
                        break
                else:
                    result = bone_name
                    break
        return result
    
    
    def _clear_bone_name_lower(self, name: str) -> str:
        return "".join(["_" + c.lower() if c.isupper() else c.lower() for c in name]).strip()


class DWPOSE_BONE_OT_clear_body_bones(Operator):
    bl_idname = "object.clear_body_bones"
    bl_label = "Clear body bones"
    bl_description = "Clear all body bones."
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        props = context.scene.dwpose_map_props
        self._clear_bones(props)
        self.report({'INFO'}, "The bone fields were successfully cleared.")
        return {'FINISHED'}
    
    
    def _clear_bones(self, props):
        props.bone_nose = ""
        props.bone_neck = ""
        props.bone_eye_l = ""
        props.bone_eye_r = ""
        props.bone_ear_l = ""
        props.bone_ear_r = ""
        props.bone_shoulder_l = ""
        props.bone_shoulder_r = ""
        props.bone_elbow_l = ""
        props.bone_elbow_r = ""
        props.bone_wrist_l = ""
        props.bone_wrist_r = ""
        props.bone_thigh_l = ""
        props.bone_thigh_r = ""
        props.bone_knee_l = ""
        props.bone_knee_r = ""
        props.bone_foot_l = ""
        props.bone_foot_r = ""
        props.bone_toe_l = ""
        props.bone_toe_r = ""
        props.bone_heel_l = ""
        props.bone_heel_r = ""


class DWPOSE_BONE_OT_clear_hand_bones(Operator):
    bl_idname = "object.clear_hand_bones"
    bl_label = "Clear hand bones"
    bl_description = "Clear all hand bones."
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        props = context.scene.dwpose_map_props
        self._clear_bones(props)
        self.report({'INFO'}, "The bone fields were successfully cleared.")
        return {'FINISHED'}
    
    
    def _clear_bones(self, props):
        props.bone_hand_l = ""
        props.bone_hand_r = ""
        props.bone_hand_l_thumb1 = ""
        props.bone_hand_r_thumb1 = ""
        props.bone_hand_l_thumb2 = ""
        props.bone_hand_r_thumb2 = ""
        props.bone_hand_l_thumb3 = ""
        props.bone_hand_r_thumb3 = ""
        props.bone_hand_l_thumb4 = ""
        props.bone_hand_r_thumb4 = ""
        props.bone_hand_l_index1 = ""
        props.bone_hand_r_index1 = ""
        props.bone_hand_l_index2 = ""
        props.bone_hand_r_index2 = ""
        props.bone_hand_l_index3 = ""
        props.bone_hand_r_index3 = ""
        props.bone_hand_l_index4 = ""
        props.bone_hand_r_index4 = ""
        props.bone_hand_l_middle1 = ""
        props.bone_hand_r_middle1 = ""
        props.bone_hand_l_middle2 = ""
        props.bone_hand_r_middle2 = ""
        props.bone_hand_l_middle3 = ""
        props.bone_hand_r_middle3 = ""
        props.bone_hand_l_middle4 = ""
        props.bone_hand_r_middle4 = ""
        props.bone_hand_l_ring1 = ""
        props.bone_hand_r_ring1 = ""
        props.bone_hand_l_ring2 = ""
        props.bone_hand_r_ring2 = ""
        props.bone_hand_l_ring3 = ""
        props.bone_hand_r_ring3 = ""
        props.bone_hand_l_ring4 = ""
        props.bone_hand_r_ring4 = ""
        props.bone_hand_l_pinky1 = ""
        props.bone_hand_r_pinky1 = ""
        props.bone_hand_l_pinky2 = ""
        props.bone_hand_r_pinky2 = ""
        props.bone_hand_l_pinky3 = ""
        props.bone_hand_r_pinky3 = ""
        props.bone_hand_l_pinky4 = ""
        props.bone_hand_r_pinky4 = ""
