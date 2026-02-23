from bpy.types import Panel


class DWPOSE_PT_setup_panel(Panel):
    bl_label = "DWPose Map"
    bl_idname = "DWPOSE_PT_setup_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DWPose Map'


    def draw(self, context):
        layout = self.layout
        props = context.scene.dwpose_map_props
        column_layout = layout.column(align=True)
        self._draw_panel_select_armature(props, column_layout)
        column_layout.separator()
        self._draw_panel_bones(props, column_layout)
        column_layout.separator()
        self._draw_panel_settings(props, column_layout)
        column_layout.separator()
        self._draw_panel_create_dwpose(column_layout)
        column_layout.separator()
        self._draw_panel_scene_setup(column_layout)
        column_layout.separator()
        self._draw_panel_info(column_layout)


    def _draw_panel_select_armature(self, props, current_layout):
        panel_header, panel_layout = current_layout.panel("panel_select_armature", default_closed=False)
        panel_header.label(text="1. Select armature", icon='OUTLINER_OB_ARMATURE')
        if panel_layout:
            column_layout = panel_layout.column(align=True) 
            column_layout.prop(props, "armature", text="")


    def _draw_panel_bones(self, props, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_bones", default_closed=True)
        panel_header.label(text="2. Select bones", icon='BONE_DATA')
        if panel_layout:
            if props.armature:
                column_layout = panel_layout.column(align=True)
                column_layout.separator()
                column_layout.operator("object.auto_setup_bones")
                column_layout.separator()
                column_layout.prop_search(props, "bone_head", props.armature.data, "bones", text="Head")
                column_layout.separator()
                column_layout.prop(props, "body_enable")
                if props.body_enable:
                    column_layout.separator()
                    self._draw_body_bones(props, column_layout)
                column_layout.separator()
                column_layout.prop(props, "hands_enable")
                if props.hands_enable:
                    column_layout.separator()
                    self._draw_hands_bones(props, column_layout)
                #column_layout.separator()
                #column_layout.prop(props, "face_enable")
            else:
                panel_layout.label(text="First select the armature!", icon='ERROR')
            
            
    def _draw_body_bones(self, props, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_body_bones", default_closed=True)
        panel_header.label(text="Body bones")
        if panel_layout:
            panel_layout.separator()
            panel_layout.operator("object.clear_body_bones")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_nose", props.armature.data, "bones", text="Nose")
            panel_layout.prop_search(props, "bone_eye_l", props.armature.data, "bones", text="Left Eye")
            panel_layout.prop_search(props, "bone_ear_l", props.armature.data, "bones", text="Left Ear")
            panel_layout.prop_search(props, "bone_eye_r", props.armature.data, "bones", text="Right Eye")
            panel_layout.prop_search(props, "bone_ear_r", props.armature.data, "bones", text="Right Ear")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_neck", props.armature.data, "bones", text="Neck")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_shoulder_l", props.armature.data, "bones", text="Left Shoulder")
            panel_layout.prop_search(props, "bone_elbow_l", props.armature.data, "bones", text="Left Elbow")
            panel_layout.prop_search(props, "bone_wrist_l", props.armature.data, "bones", text="Left Wrist")
            panel_layout.prop_search(props, "bone_shoulder_r", props.armature.data, "bones", text="Right Shoulder")
            panel_layout.prop_search(props, "bone_elbow_r", props.armature.data, "bones", text="Right Elbow")
            panel_layout.prop_search(props, "bone_wrist_r", props.armature.data, "bones", text="Right Wrist")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_thigh_l", props.armature.data, "bones", text="Left Thigh")
            panel_layout.prop_search(props, "bone_knee_l", props.armature.data, "bones", text="Left Knee")
            panel_layout.prop_search(props, "bone_foot_l", props.armature.data, "bones", text="Left Foot")
            panel_layout.prop_search(props, "bone_toe_l", props.armature.data, "bones", text="Left Toe")
            panel_layout.prop_search(props, "bone_heel_l", props.armature.data, "bones", text="Left Heel")
            panel_layout.prop_search(props, "bone_thigh_r", props.armature.data, "bones", text="Right Thigh")
            panel_layout.prop_search(props, "bone_knee_r", props.armature.data, "bones", text="Right Knee")
            panel_layout.prop_search(props, "bone_foot_r", props.armature.data, "bones", text="Right Foot")
            panel_layout.prop_search(props, "bone_toe_r", props.armature.data, "bones", text="Right Toe")
            panel_layout.prop_search(props, "bone_heel_r", props.armature.data, "bones", text="Right Heel")
    
    
    def _draw_hands_bones(self, props, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_hands_bones", default_closed=True)
        panel_header.label(text="Hands bones")
        if panel_layout:
            panel_layout.separator()
            panel_layout.operator("object.clear_hand_bones")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l", props.armature.data, "bones", text="Left Hand")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l_thumb1", props.armature.data, "bones", text="Left Thumb1")
            panel_layout.prop_search(props, "bone_hand_l_thumb2", props.armature.data, "bones", text="Left Thumb2")
            panel_layout.prop_search(props, "bone_hand_l_thumb3", props.armature.data, "bones", text="Left Thumb3")
            panel_layout.prop_search(props, "bone_hand_l_thumb4", props.armature.data, "bones", text="Left Thumb4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l_index1", props.armature.data, "bones", text="Left Index1")
            panel_layout.prop_search(props, "bone_hand_l_index2", props.armature.data, "bones", text="Left Index2")
            panel_layout.prop_search(props, "bone_hand_l_index3", props.armature.data, "bones", text="Left Index3")
            panel_layout.prop_search(props, "bone_hand_l_index4", props.armature.data, "bones", text="Left Index4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l_middle1", props.armature.data, "bones", text="Left Middle1")
            panel_layout.prop_search(props, "bone_hand_l_middle2", props.armature.data, "bones", text="Left Middle2")
            panel_layout.prop_search(props, "bone_hand_l_middle3", props.armature.data, "bones", text="Left Middle3")
            panel_layout.prop_search(props, "bone_hand_l_middle4", props.armature.data, "bones", text="Left Middle4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l_ring1", props.armature.data, "bones", text="Left Ring1")
            panel_layout.prop_search(props, "bone_hand_l_ring2", props.armature.data, "bones", text="Left Ring2")
            panel_layout.prop_search(props, "bone_hand_l_ring3", props.armature.data, "bones", text="Left Ring3")
            panel_layout.prop_search(props, "bone_hand_l_ring4", props.armature.data, "bones", text="Left Ring4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_l_pinky1", props.armature.data, "bones", text="Left Pinky1")
            panel_layout.prop_search(props, "bone_hand_l_pinky2", props.armature.data, "bones", text="Left Pinky2")
            panel_layout.prop_search(props, "bone_hand_l_pinky3", props.armature.data, "bones", text="Left Pinky3")
            panel_layout.prop_search(props, "bone_hand_l_pinky4", props.armature.data, "bones", text="Left Pinky4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r", props.armature.data, "bones", text="Right Hand")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r_thumb1", props.armature.data, "bones", text="Right Thumb1")
            panel_layout.prop_search(props, "bone_hand_r_thumb2", props.armature.data, "bones", text="Right Thumb2")
            panel_layout.prop_search(props, "bone_hand_r_thumb3", props.armature.data, "bones", text="Right Thumb3")
            panel_layout.prop_search(props, "bone_hand_r_thumb4", props.armature.data, "bones", text="Right Thumb4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r_index1", props.armature.data, "bones", text="Right Index1")
            panel_layout.prop_search(props, "bone_hand_r_index2", props.armature.data, "bones", text="Right Index2")
            panel_layout.prop_search(props, "bone_hand_r_index3", props.armature.data, "bones", text="Right Index3")
            panel_layout.prop_search(props, "bone_hand_r_index4", props.armature.data, "bones", text="Right Index4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r_middle1", props.armature.data, "bones", text="Right Middle1")
            panel_layout.prop_search(props, "bone_hand_r_middle2", props.armature.data, "bones", text="Right Middle2")
            panel_layout.prop_search(props, "bone_hand_r_middle3", props.armature.data, "bones", text="Right Middle3")
            panel_layout.prop_search(props, "bone_hand_r_middle4", props.armature.data, "bones", text="Right Middle4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r_ring1", props.armature.data, "bones", text="Right Ring1")
            panel_layout.prop_search(props, "bone_hand_r_ring2", props.armature.data, "bones", text="Right Ring2")
            panel_layout.prop_search(props, "bone_hand_r_ring3", props.armature.data, "bones", text="Right Ring3")
            panel_layout.prop_search(props, "bone_hand_r_ring4", props.armature.data, "bones", text="Right Ring4")
            panel_layout.separator()
            panel_layout.prop_search(props, "bone_hand_r_pinky1", props.armature.data, "bones", text="Right Pinky1")
            panel_layout.prop_search(props, "bone_hand_r_pinky2", props.armature.data, "bones", text="Right Pinky2")
            panel_layout.prop_search(props, "bone_hand_r_pinky3", props.armature.data, "bones", text="Right Pinky3")
            panel_layout.prop_search(props, "bone_hand_r_pinky4", props.armature.data, "bones", text="Right Pinky4")
    
    
    def _draw_panel_settings(self, props, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_settings", default_closed=True)
        panel_header.label(text="3. Settings (Optional)", icon='SETTINGS')
        if panel_layout:
            panel_layout.separator()
            panel_layout.prop(props, "body_points_radius")
            panel_layout.prop(props, "body_lines_radius")
            panel_layout.separator()
            panel_layout.prop(props, "hands_points_radius")
            panel_layout.prop(props, "hands_lines_radius")
            panel_layout.separator()
            panel_layout.prop(props, "face_points_radius")
            panel_layout.separator()
    
    
    def _draw_panel_create_dwpose(self, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_create_dwpose", default_closed=True)
        panel_header.label(text="4. Create DWPose", icon='ARMATURE_DATA')
        if panel_layout:
            panel_layout.separator()
            panel_layout.operator("object.create_dwpose")
            panel_layout.separator()
    
    
    def _draw_panel_scene_setup(self, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_scene_setup", default_closed=True)
        panel_header.label(text="5. Setup scene (Optional)", icon='SCENE')
        if panel_layout:
            panel_layout.separator()
            panel_layout.operator("object.setup_scene_for_dwpose_render")
            panel_layout.separator()
    
    
    def _draw_panel_info(self, parent_layout):
        panel_header, panel_layout = parent_layout.panel("panel_info", default_closed=True)
        panel_header.label(text="6. More info", icon='INFO')
        if panel_layout:
            panel_layout.label(text="If necessary, manually correct the position of the markers.")

