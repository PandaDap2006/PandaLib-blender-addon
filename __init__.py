from .src.prompts import MeshExportPrompt

bl_info = {
	"name": "Minecraft Pandalib Blender Addon",
	"author": "Panda Mods / The Panda Oliver",
	"description": "",
	"blender": (3, 5, 1),
	"version": (0, 1, 0),
	"location": "",
	"warning": "",
	"category": "Generic"
}


mesh_version = "0.5"
armature_version = "0.5"
animation_version = "0.5"


def register():
	MeshExportPrompt.register()


def unregister():
	MeshExportPrompt.unregister()
