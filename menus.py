# Copyright 2017 Integrity Software and Games, LLC
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of UltiMaze.
#
# UltiMaze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltiMaze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltiMaze.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import os

import bpy


class TileRenderMenu(bpy.types.Menu):
    bl_idname = "maze_gen.tile_render_menu"
    bl_label = "Render Previews"

    def draw(self, context):
        mg = context.scene.mg
        addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences

        # get tile blend file names
        files_list = os.listdir(addon_prefs.tiles_path)
        tile_blends = [a[:-6] for a in files_list if a.endswith('.blend') and a[-7] in ("2", "6")]
        tile_pngs = [a[:-4] for a in files_list if a.endswith('.png') and a[:-4] in tile_blends]

        # user interface
        layout = self.layout

        for tileset in tile_blends:
            has_png = True
            t = tileset
            if tileset not in tile_pngs:
                t = "* " + t  # show an asterisk if the file doesn't have a corresponding png
                has_png = False
            button = layout.operator("maze_gen.render_tileset", text=t)
            button.filename = os.path.join(addon_prefs.tiles_path, tileset + ".blend")
            button.has_png = has_png


class EnableLayerMenu(bpy.types.Menu):
    bl_idname = "maze_gen.enable_layer_menu"
    bl_label = "Layer 1 must be enabled!"

    def draw(self, context):
        layout = self.layout
        layout.operator("maze_gen.enable_layer")
