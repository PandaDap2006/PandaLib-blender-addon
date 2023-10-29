import json
from math import degrees

import bpy


def exportAnimation(context, filepath, self):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(json.dumps(createJson(self), indent=2))
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """This exports the Animation for use with PandaLib"""
    bl_idname = "pandamods.export_animation"
    bl_label = "Export Rig"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return exportAnimation(context, self.filepath, self)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="PandaLib animation (.json)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

def createJson(self):
    scene = bpy.context.scene
    jsonAnimation = {
        "format_version": "0.1",
        "animation_length": convertToSecond(scene.frame_end),
        "bones": createBone(self)
    }
    return jsonAnimation


def createBone(self):
    bonesDict = {}

    armature = bpy.data.objects["Armature"]
    action = armature.animation_data.action
    for group in action.groups:
        position = {}
        rotation = {}
        scale = {}

        for channel in group.channels:
            for keyframe in channel.keyframe_points:
                if "location" in channel.data_path:
                    if convertToSecond(keyframe.co[0]) not in position.keys():
                        position[convertToSecond(keyframe.co[0])] = [0, 0, 0]
                    position[convertToSecond(keyframe.co[0])][channel.array_index] = keyframe.co[1]
                elif "rotation_euler" in channel.data_path:
                    if convertToSecond(keyframe.co[0]) not in rotation.keys():
                        rotation[convertToSecond(keyframe.co[0])] = [0, 0, 0]
                    if channel.array_index != 0:
                        rotation[convertToSecond(keyframe.co[0])][channel.array_index] = -degrees(
                            keyframe.co[1])
                    else:
                        rotation[convertToSecond(keyframe.co[0])][channel.array_index] = degrees(
                            keyframe.co[1])
                elif "scale" in channel.data_path:
                    if convertToSecond(keyframe.co[0]) not in scale.keys():
                        scale[convertToSecond(keyframe.co[0])] = [0, 0, 0]
                    scale[convertToSecond(keyframe.co[0])][channel.array_index] = keyframe.co[1]
                elif "rotation_quaternion" in channel.data_path:
                    self.report({"ERROR"}, "Please only use Euler Rotations")

        boneDict = {"position": position, "rotation": rotation, "scale": scale}
        bonesDict[group.name] = boneDict

    return bonesDict

def convertToSecond(frame):
    scene = bpy.context.scene
    fps = scene.render.fps
    return frame / fps