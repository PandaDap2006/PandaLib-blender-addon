import json
from array import array
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from mathutils import Quaternion
from .. import BakeAnimation

animation_version = "0.2"


def export(context, filepath, self, bake):
    if bake:
        BakeAnimation.bake()

    f = open(filepath, 'w', encoding='utf-8')
    f.write(json.dumps(createJson(self), indent=2))
    f.close()

    return {'FINISHED'}


class ExportSomeData(Operator, ExportHelper):
    """This exports the Animation for use with PandaLib"""
    bl_idname = "pandamods.export_animation"
    bl_label = "Export Animation"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    bake: BoolProperty(
        name="Bake",
        description="Should bake the animation before exporting",
        default=False
    )

    def execute(self, context):
        return export(context, self.filepath, self, self.bake)


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
        "format_version": animation_version,
        "animation_length": convertToSecond(scene.frame_end),
        "bones": createBone(self)
    }
    return jsonAnimation


def createBone(self):
    bonesDict = {}

    armatureOBJ = bpy.data.objects["Armature"]
    action = armatureOBJ.animation_data.action
    scene = bpy.context.scene
    for group in action.groups:
        positionKeys = array("i")
        rotationKeys = array("i")
        scaleKeys = array("i")

        positions = {}
        rotations = {}
        scales = {}

        for channel in group.channels:
            for keyframe in channel.keyframe_points:
                frame = int(keyframe.co[0])
                if "location" in channel.data_path and positionKeys.__contains__(frame) is False:
                    positionKeys.append(frame)
                if (("rotation_euler" in channel.data_path or "rotation_quaternion" in channel.data_path)
                        and rotationKeys.__contains__(frame) is False):
                    rotationKeys.append(frame)
                if "scale" in channel.data_path and scaleKeys.__contains__(frame) is False:
                    scaleKeys.append(frame)

        poseBone = armatureOBJ.pose.bones[group.name]
        matrix = poseBone.matrix_basis

        for positionKey in positionKeys:
            scene.frame_set(positionKey)
            vector = matrix.to_translation()
            positions[convertToSecond(positionKey)] = [vector.x, vector.y, vector.z]

        for rotationKey in rotationKeys:
            scene.frame_set(rotationKey)
            quaternion = Quaternion(matrix.to_quaternion())
            rotations[convertToSecond(rotationKey)] = [quaternion.w, quaternion.x, quaternion.y, quaternion.z]

        for scaleKey in scaleKeys:
            scene.frame_set(scaleKey)
            vector = matrix.to_scale()
            scales[convertToSecond(scaleKey)] = [vector.x, vector.y, vector.z]

        boneDict = {"position": positions, "rotation": rotations, "scale": scales}
        bonesDict[group.name] = boneDict

    return bonesDict


def convertToSecond(frame):
    scene = bpy.context.scene
    fps = scene.render.fps
    return frame / fps
