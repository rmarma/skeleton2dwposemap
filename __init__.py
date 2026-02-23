import bpy
from bpy.props import PointerProperty
from . import properties, ui, operators


_CLASSES = [
    properties.DWPoseMapProperties,
    ui.DWPOSE_PT_setup_panel,
    operators.DWPOSE_SCENE_OT_setup_scene_for_dwpose_render,
    operators.DWPOSE_BONES_OT_create_dwpose,
    operators.DWPOSE_BONE_OT_auto_setup_bones,
    operators.DWPOSE_BONE_OT_clear_body_bones,
    operators.DWPOSE_BONE_OT_clear_hand_bones,
]


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dwpose_map_props = PointerProperty(type=properties.DWPoseMapProperties)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.dwpose_map_props
