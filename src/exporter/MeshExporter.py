import bpy
import json
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator

mesh_version = "0.4"


def export(context, filepath, self):
	f = open(filepath, 'w', encoding='utf-8')
	f.write(json.dumps(createJson(self), indent=2))
	f.close()

	return {'FINISHED'}


class ExportSomeData(Operator, ExportHelper):
	"""This exports the Mesh for use with PandaLib"""
	bl_idname = "pandamods.export_mesh"
	bl_label = "Export Mesh"

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
	self.layout.operator(ExportSomeData.bl_idname, text="PandaLib Mesh (.json)")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
	bpy.utils.register_class(ExportSomeData)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportSomeData)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def createJson(self):
	return {
		"format_version": mesh_version,
		"objects": createMesh(self)
	}


def createMesh(self):
	meshJson = {}
	notQuadCount = 0
	for object in bpy.data.objects:
		if object.type == "MESH":
			vertexGroups = {g.index: g.name for g in object.vertex_groups}
			mesh = object.to_mesh()

			vertexList = []
			for vertex in mesh.vertices:
				maxWeight = 0
				groupsList = []
				for group in vertex.groups:
					groupDict = {
						"name": vertexGroups[group.group],
						"weight": group.weight
					}
					maxWeight += group.weight
					groupsList.append(groupDict)

				vertexList.append({
					"index": vertex.index,
					"position": [vertex.co.x, vertex.co.z, -vertex.co.y],
					"weights": groupsList,
					"max_weight": maxWeight
				})

			faceList = []
			for face in mesh.polygons:
				if len(face.vertices) == 4:
					uvs = {}
					for uvIndex in face.loop_indices:
						vertex_index = mesh.loops[uvIndex].vertex_index
						uv = mesh.uv_layers.active.data[uvIndex].uv
						uvs[vertex_index] = [uv.x, uv.y]

					vertexIndexList = []
					for vertexIndex in face.vertices:
						vertexIndexList.append(vertexIndex)

					faceList.append({
						"normal": [face.normal.x, face.normal.z, -face.normal.y],
						"vertices": vertexIndexList,
						"vertex_uvs": uvs,
						"texture_name": object.material_slots[face.material_index].name
					})
				else:
					notQuadCount += 1

			objectMatrix = object.matrix_world
			meshJson[object.name] = {
				"position": [objectMatrix.translation.x, objectMatrix.translation.z, -objectMatrix.translation.y],
				"rotation": [objectMatrix.to_quaternion().x, objectMatrix.to_quaternion().y, objectMatrix.to_quaternion().z, objectMatrix.to_quaternion().w],
				"vertices": vertexList,
				"faces": faceList
			}

	if notQuadCount > 0:
		self.report({"ERROR"}, str(notQuadCount) + " faces was not quad")
		self.report({"ERROR"}, "Please only use 4 vertices for each face")
	return meshJson
