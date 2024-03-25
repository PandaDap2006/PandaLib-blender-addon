import json
from mathutils import Vector
from ...__init__ import mesh_version
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator


class MeshExportPrompt(Operator, ExportHelper):
	"""This exports the Mesh for use with PandaLib"""
	bl_idname = "pandamods.export_mesh"
	bl_label = "Export Mesh"

	filename_ext = ".json"

	filter_glob: StringProperty(
		default="*.json",
		options={'HIDDEN'},
		maxlen=255,  # Max internal buffer length, longer would be clamped.
	)

	def execute(self, context):
		file = open(self.filepath, 'w', encoding='utf-8')
		file.write(json.dumps(createJson(self), indent=2))
		file.close()
		return {'FINISHED'}


def createJson(self):
	vertices = []
	faces = []
	notQuadCount = 0

	for obj in bpy.data.objects:
		vertexOffset = len(vertices)
		if obj.type == "MESH":
			vertexGroups = {group.index: group.name for group in obj.vertex_groups}
			mesh = obj.to_mesh()

			for vertex in mesh.vertices:
				maxWeight = 0
				weights = []
				for weight in vertex.groups:
					maxWeight += weight.weight
					weights.append({
						"name": vertexGroups[weight.group],
						"weight": weight.weight
					})

				position = vertex.co + obj.matrix_world.to_translation()
				position.rotate(obj.matrix_world.to_quaternion())
				vertices.append({
					"position": [position.x, position.z, -position.y],
					"weights": weights,
					"max_weight": maxWeight
				})

			for polygon in mesh.polygons:
				if len(polygon.vertices) == 4:
					faceVertices = []
					for uvIndex in polygon.loop_indices:
						vertex_index = mesh.loops[uvIndex].vertex_index
						uv = mesh.uv_layers.active.data[uvIndex].uv
						faceVertices.append({
							"index": vertex_index + vertexOffset,
							"uv": [uv.x, uv.y]
						})

					# vertexIndexList = []
					# for vertexIndex in polygon.vertices:
					# 	vertexIndexList.append(vertexIndex + vertexOffset)

					normal = Vector(polygon.normal)
					normal.rotate(obj.matrix_world.to_quaternion())
					textureName = obj.material_slots[polygon.material_index].name
					faces.append({
						"normal": [normal.x, normal.z, -normal.y],
						"vertices": faceVertices,
						"texture_name": textureName
					})
				else:
					notQuadCount += 1

	if notQuadCount > 0:
		self.report({"ERROR"}, str(notQuadCount) + " faces was not quad")
		self.report({"ERROR"}, "Please only use 4 vertices for each face")
	return {
		"format_version": mesh_version,
		"vertices": vertices,
		"faces": faces,
	}

def menu_func_export(self, context):
	self.layout.operator(MeshExportPrompt.bl_idname, text="PandaLib Mesh (.json)")


def register():
	bpy.utils.register_class(MeshExportPrompt)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(MeshExportPrompt)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)