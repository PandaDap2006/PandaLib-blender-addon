# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from exporter import MeshExporter, AnimationExporter, ArmatureExporter

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
