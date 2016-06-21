import os

import bpy


class TileImportMenu(bpy.types.Menu):
    bl_idname = "maze_gen.tile_import_menu"
    bl_label = "Import Tile Set"

    def draw(self, context):
        scene = context.scene
        addon_prefs = context.user_preferences.addons['maze_gen'].preferences

        # get file names
        files_list = os.listdir(os.path.join(os.path.dirname(__file__), "tiles"))
        if addon_prefs.use_custom_tile_path:
            try:
                files_list += os.listdir(addon_prefs.custom_tile_path)
            except FileNotFoundError:
                print("Invalid custom tile path!")

        if scene.tile_mode == "TWELVE_TILES":
            tile_blends = [a for a in files_list if a[-6:] == '.blend' and a[:-6][-1:] == "2"]
        elif scene.tile_mode == "SIX_TILES":
            tile_blends = [a for a in files_list if a[-6:] == '.blend' and a[:-6][-1:] == "6"]
        layout = self.layout
        for tileset in tile_blends:
            layout.operator("maze_gen.import_tileset", text=tileset[:-7]).filename = tileset


class EnableLayerMenu(bpy.types.Menu):
    bl_idname = "maze_gen.enable_layer_menu"
    bl_label = "Layer 1 must be enabled!"

    def draw(self, context):
        layout = self.layout
        layout.operator("maze_gen.enable_layer")


class SaveUserPrefsMenu(bpy.types.Menu):
    bl_idname = "maze_gen.save_user_prefs_menu"
    bl_label = "Save user settings."

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Sorry, your OS doesn't support")
        row = layout.row()
        row.label(text="opening files outside of Blender.")
        row = layout.row()
        row.label(text="Please save user settings.")

        layout.operator("wm.save_userpref", text="Save User Prefs")
