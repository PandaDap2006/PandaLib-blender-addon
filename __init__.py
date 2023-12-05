from .src.exporter import ArmatureExporter, MeshExporter, AnimationExporter

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


def register():
    MeshExporter.register()
    ArmatureExporter.register()
    AnimationExporter.register()


def unregister():
    MeshExporter.unregister()
    ArmatureExporter.unregister()
    AnimationExporter.unregister()
