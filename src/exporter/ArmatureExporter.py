import bpy
import json
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator


armature_version = "0.1"


def export(context, filepath, self):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(json.dumps(createJson(self), indent=2))
    f.close()

    return {'FINISHED'}


class ExportSomeData(Operator, ExportHelper):
    """This exports the Armature for use with PandaLib"""
    bl_idname = "pandamods.export_armature"
    bl_label = "Export Armature"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return export(context, self.filepath, self)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="PandaLib Armature (.json)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def createJson(self):
    return {
        "format_version": armature_version,
        "bones": createBones()
    }


def createBones():
    bonesDict = {}

    for object in bpy.data.objects:
        if object.type == "ARMATURE":
            armature: bpy.types.Armature = object.data
            bpy.context.view_layer.objects.active = object
            bpy.ops.object.mode_set(mode="EDIT")
            for bone in armature.edit_bones:
                head = bone.head
                boneDict = {
                    "position": [head.x, head.z, -head.y]
                }

                if bone.parent is not None:
                    boneDict["parent"] = bone.parent.name

                bonesDict[bone.name] = boneDict
            bpy.ops.object.mode_set(mode="OBJECT")
            break
    return bonesDict
