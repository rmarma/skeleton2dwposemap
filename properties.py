import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, FloatProperty
from bpy.types import PropertyGroup


class DWPoseMapProperties(PropertyGroup):
    armature: PointerProperty(
        type=bpy.types.Object,
        name="Target Armature",
        description="Select the armature object.",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    body_enable: BoolProperty(name="Body", description="Display the body in DWPose", default=True)
    hands_enable: BoolProperty(name="Hands", description="Display the hands in DWPose", default=False)
    face_enable: BoolProperty(name="Face", description="Display the face in DWPose", default=False)
    body_points_radius: FloatProperty(
        name="Body points radius",
        description="Sets the radius of points when displaying the body skeleton in DWPose.",
        default=0.02,
        min=0.0,
        precision=3
    )
    hands_points_radius: FloatProperty(
        name="Hands points radius",
        description="Sets the radius of points when displaying the hands skeleton in DWPose.",
        default=0.01,
        min=0.0,
        precision=3
    )
    face_points_radius: FloatProperty(
        name="Face points radius",
        description="Sets the radius of points when displaying the face skeleton in DWPose.",
        default=0.015,
        min=0.0,
        precision=3
    )
    body_lines_radius: FloatProperty(
        name="Body lines radius",
        description="Sets the radius of lines when displaying the body skeleton in DWPose.",
        default=0.015,
        min=0.0,
        precision=3
    )
    hands_lines_radius: FloatProperty(
        name="Hands lines radius",
        description="Sets the radius of lines when displaying the hands skeleton in DWPose.",
        default=0.005,
        min=0.0,
        precision=3
    )
    bone_head: StringProperty(name="Head bone", description="Select the head bone.")
    bone_nose: StringProperty(name="Nose bone", description="Select the nose bone.")
    bone_eye_l: StringProperty(name="Left eye bone", description="Select the left eye bone.")
    bone_ear_l: StringProperty(name="Left ear bone", description="Select the left ear bone.")
    bone_eye_r: StringProperty(name="Right eye bone", description="Select the right eye bone.")
    bone_ear_r: StringProperty(name="Right ear bone", description="Select the right ear bone.")
    bone_neck: StringProperty(name="Neck bone", description="Select the neck bone.")
    bone_shoulder_l: StringProperty(name="Left shoulder bone", description="Select the left shoulder bone.")
    bone_elbow_l: StringProperty(name="Left elbow bone", description="Select the left elbow bone.")
    bone_wrist_l: StringProperty(name="Left wrist bone", description="Select the left wrist bone.")
    bone_shoulder_r: StringProperty(name="Right shoulder bone", description="Select the right shoulder bone.")
    bone_elbow_r: StringProperty(name="Right elbow bone", description="Select the right elbow bone.")
    bone_wrist_r: StringProperty(name="Right wrist bone", description="Select the right wrist bone.")
    bone_thigh_l: StringProperty(name="Left thigh bone", description="Select the left thigh bone.")
    bone_knee_l: StringProperty(name="Left knee bone", description="Select the left knee bone.")
    bone_foot_l: StringProperty(name="Left foot bone", description="Select the left foot bone.")
    bone_toe_l: StringProperty(name="Left toe bone", description="Select the left toe bone.")
    bone_heel_l: StringProperty(name="Left heel bone", description="Select the left heel bone.")
    bone_thigh_r: StringProperty(name="Right thigh bone", description="Select the right thigh bone.")
    bone_knee_r: StringProperty(name="Right knee bone", description="Select the right knee bone.")
    bone_foot_r: StringProperty(name="Right foot bone", description="Select the right foot bone.")
    bone_toe_r: StringProperty(name="Right toe bone", description="Select the right toe bone.")
    bone_heel_r: StringProperty(name="Right heel bone", description="Select the right heel bone.")
    bone_hand_l: StringProperty(name="Left hand bone", description="Select the left hand bone.")
    bone_hand_l_thumb1: StringProperty(name="Left hand thumb1 bone", description="Select the left hand thumb1 bone.")
    bone_hand_l_thumb2: StringProperty(name="Left hand thumb2 bone", description="Select the left hand thumb2 bone.")
    bone_hand_l_thumb3: StringProperty(name="Left hand thumb3 bone", description="Select the left hand thumb3 bone.")
    bone_hand_l_thumb4: StringProperty(name="Left hand thumb4 bone", description="Select the left hand thumb4 bone.")
    bone_hand_l_index1: StringProperty(name="Left hand index1 bone", description="Select the left hand index1 bone.")
    bone_hand_l_index2: StringProperty(name="Left hand index2 bone", description="Select the left hand index2 bone.")
    bone_hand_l_index3: StringProperty(name="Left hand index3 bone", description="Select the left hand index3 bone.")
    bone_hand_l_index4: StringProperty(name="Left hand index4 bone", description="Select the left hand index4 bone.")
    bone_hand_l_middle1: StringProperty(name="Left hand middle1 bone", description="Select the left hand middle1 bone.")
    bone_hand_l_middle2: StringProperty(name="Left hand middle2 bone", description="Select the left hand middle2 bone.")
    bone_hand_l_middle3: StringProperty(name="Left hand middle3 bone", description="Select the left hand middle3 bone.")
    bone_hand_l_middle4: StringProperty(name="Left hand middle4 bone", description="Select the left hand middle4 bone.")
    bone_hand_l_ring1: StringProperty(name="Left hand ring1 bone", description="Select the left hand ring1 bone.")
    bone_hand_l_ring2: StringProperty(name="Left hand ring2 bone", description="Select the left hand ring2 bone.")
    bone_hand_l_ring3: StringProperty(name="Left hand ring3 bone", description="Select the left hand ring3 bone.")
    bone_hand_l_ring4: StringProperty(name="Left hand ring4 bone", description="Select the left hand ring4 bone.")
    bone_hand_l_pinky1: StringProperty(name="Left hand pinky1 bone", description="Select the left hand pinky1 bone.")
    bone_hand_l_pinky2: StringProperty(name="Left hand pinky2 bone", description="Select the left hand pinky2 bone.")
    bone_hand_l_pinky3: StringProperty(name="Left hand pinky3 bone", description="Select the left hand pinky3 bone.")
    bone_hand_l_pinky4: StringProperty(name="Left hand pinky4 bone", description="Select the left hand pinky4 bone.")
    bone_hand_r: StringProperty(name="Right hand bone", description="Select the right hand bone.")
    bone_hand_r_thumb1: StringProperty(name="Right hand thumb1 bone", description="Select the right hand thumb1 bone.")
    bone_hand_r_thumb2: StringProperty(name="Right hand thumb2 bone", description="Select the right hand thumb2 bone.")
    bone_hand_r_thumb3: StringProperty(name="Right hand thumb3 bone", description="Select the right hand thumb3 bone.")
    bone_hand_r_thumb4: StringProperty(name="Right hand thumb4 bone", description="Select the right hand thumb4 bone.")
    bone_hand_r_index1: StringProperty(name="Right hand index1 bone", description="Select the right hand index1 bone.")
    bone_hand_r_index2: StringProperty(name="Right hand index2 bone", description="Select the right hand index2 bone.")
    bone_hand_r_index3: StringProperty(name="Right hand index3 bone", description="Select the right hand index3 bone.")
    bone_hand_r_index4: StringProperty(name="Right hand index4 bone", description="Select the right hand index4 bone.")
    bone_hand_r_middle1: StringProperty(name="Right hand middle1 bone", description="Select the right hand middle1 bone.")
    bone_hand_r_middle2: StringProperty(name="Right hand middle2 bone", description="Select the right hand middle2 bone.")
    bone_hand_r_middle3: StringProperty(name="Right hand middle3 bone", description="Select the right hand middle3 bone.")
    bone_hand_r_middle4: StringProperty(name="Right hand middle4 bone", description="Select the right hand middle4 bone.")
    bone_hand_r_ring1: StringProperty(name="Right hand ring1 bone", description="Select the right hand ring1 bone.")
    bone_hand_r_ring2: StringProperty(name="Right hand ring2 bone", description="Select the right hand ring2 bone.")
    bone_hand_r_ring3: StringProperty(name="Right hand ring3 bone", description="Select the right hand ring3 bone.")
    bone_hand_r_ring4: StringProperty(name="Right hand ring4 bone", description="Select the right hand ring4 bone.")
    bone_hand_r_pinky1: StringProperty(name="Right hand pinky1 bone", description="Select the right hand pinky1 bone.")
    bone_hand_r_pinky2: StringProperty(name="Right hand pinky2 bone", description="Select the right hand pinky2 bone.")
    bone_hand_r_pinky3: StringProperty(name="Right hand pinky3 bone", description="Select the right hand pinky3 bone.")
    bone_hand_r_pinky4: StringProperty(name="Right hand pinky4 bone", description="Select the right hand pinky4 bone.")
