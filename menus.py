import os

import bpy


class TileRenderMenu(bpy.types.Menu):
    bl_idname = "maze_gen.tile_render_menu"
    bl_label = "Render Previews"

    def draw(self, context):
        mg = context.scene.mg

        # get tile blend file names
        files_list = os.listdir(mg.tiles_path)
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
            button.filename = os.path.join(mg.tiles_path, tileset + ".blend")
            button.has_png = has_png


class EnableLayerMenu(bpy.types.Menu):
    bl_idname = "maze_gen.enable_layer_menu"
    bl_label = "Layer 1 must be enabled!"

    def draw(self, context):
        layout = self.layout
        layout.operator("maze_gen.enable_layer")
