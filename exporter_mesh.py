import bpy
import json


def exportRig(context, filepath, self, scale):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(json.dumps(createJson(self, scale), indent=2))
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """This exports the Mesh and Armature for use with PandaLib"""
    bl_idname = "pandamods.export_rig"
    bl_label = "Export Rig"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    scale: FloatProperty(
        name="Scale",
        description="This sets the default scale of the mesh and bones",
        default=1
    )

    def execute(self, context):
        return exportRig(context, self.filepath, self, self.scale)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="PandaLib Rig (.json)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def createJson(self, scale):
    jsonRig = {
        "format_version": "0.2",
        "scale": scale,
        "objects": createMesh(self),
        "bone": createBone()
    }
    return jsonRig


def createMesh(self):
    meshJson = {}
    notQuadCount = 0
    vertexID = 0
    for object in bpy.data.objects:
        if object.type == "MESH":
            vertexGroups = {g.index: g.name for g in object.vertex_groups}
            mesh = object.data
            faceList = []

            face: bpy.types.MeshPolygon
            for face in mesh.polygons:
                if len(face.vertices) == 4:
                    verticesList = {}
                    uvs = {}
                    for uvIndex in face.loop_indices:
                        vertex_index = mesh.loops[uvIndex].vertex_index
                        uv = mesh.uv_layers.active.data[uvIndex].uv
                        uvs[vertex_index] = [uv.x, uv.y]

                    for vertexIndex in face.vertices:
                        vertex: bpy.types.MeshVertex = mesh.vertices[vertexIndex]
                        groupsList = []
                        for group in vertex.groups:
                            groupDict = {
                                "name": vertexGroups[group.group],
                                "weight": group.weight
                            }
                            groupsList.append(groupDict)

                        verticesList[vertexID] = {
                            "index": vertex.index,
                            "position": [vertex.co.x, vertex.co.z, -vertex.co.y],
                            "uv": uvs[vertex.index],
                            "weights": groupsList
                        }
                        vertexID += 1

                    faceList.append({
                        "normal": [face.normal.x, face.normal.z, -face.normal.y],
                        "vertices": verticesList,
                        "texture_name": object.material_slots[face.material_index].name
                    })
                else:
                    notQuadCount += 1
            meshJson[object.name] = {
                "position": [object.location.x, object.location.z, -object.location.y],
                "rotation": [object.rotation_euler.x, object.rotation_euler.z, -object.rotation_euler.y],
                "faces": faceList
            }
    if notQuadCount > 0:
        self.report({"ERROR"}, str(notQuadCount) + " faces was not quad")
        self.report({"ERROR"}, "Please only use 4 vertices for each face")
    return meshJson


def createBone():
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
