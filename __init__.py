# TODO - LEGAL

"""
===== MAZE GENERATOR [PRO] V.1.2 =====
This __init__ module handles some UI and also registers all
classes and properties.
"""
import os
import sys
import subprocess

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.types import Operator, Panel, Scene, AddonPreferences
from bpy.utils import register_class, unregister_class

from maze_gen import maze_gen
from maze_gen import batch_gen
from maze_gen import text_tools
from maze_gen import time_log
from maze_gen import txt_img_converter
from maze_gen import menus

bl_info = {
    "name": "UltiMaze [PRO]",
    "author": "Jake Dube",
    "version": (2, 0),
    "blender": (2, 76, 0),
    "location": "3D View > Tools > Maze Gen",
    "description": "Generates 3-dimensional mazes.",
    "warning": "May take a long time to generate maze: "
               "see quick help below.",
    "wiki_url": "",
    "category": "3D View",
}


def append_objs(path, prefix="", suffix="", case_sens=False, ignore="IGNORE"):
    """Appends all objects into scene from .blend if they meet argument criteria."""

    scene = bpy.context.scene

    with bpy.data.libraries.load(path) as (data_from, data_to):
        if not case_sens:
            data_to.objects = [name for name in data_from.objects if
                               name.lower().startswith(prefix.lower()) and name.lower().endswith(suffix.lower()) and ignore.upper() not in name.upper()]
        else:
            data_to.objects = [name for name in data_from.objects if name.startswith(prefix) and name.endswith(suffix) and ignore.upper() not in name.upper()]

    for obj in data_to.objects:
        if obj is not None:
            scene.objects.link(obj)


# UI Classes
# 3D View
class MazeGeneratorPanelMG(Panel):
    bl_label = "Maze Generator"
    bl_idname = "3D_VIEW_PT_layout_MazeGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # Generate Maze button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("maze_gen.generate_maze", icon="MOD_BUILD")

        # layout settings box
        box = layout.box()
        box.label("Layout Settings", icon='SETTINGS')
        box.prop(scene, 'mg_width', slider=False, text="Width")
        box.prop(scene, 'mg_height', slider=False, text="Height")
        box.prop(scene, 'gen_3d_maze', text="Generate 3D Maze")

        col = box.box()

        if scene.use_list_maze:
            col.enabled = False
        else:
            col.enabled = True
        row = col.row()
        row.prop(scene, 'allow_loops', text="Allow Loops")
        row.prop(scene, 'loops_chance', text="Chance")

        col.prop(scene, 'algorithm', text="", icon="OOPS")
        if scene.algorithm == 'BINARY_TREE':
            col.prop(scene, 'binary_dir', text="", icon="MOD_DECIM")
            col.prop(scene, 'tileable')

        elif scene.algorithm in ['PRIMS', 'DEPTH_FIRST', 'BREADTH_FIRST']:
            col.prop(scene, 'bias_direction', text="", icon="ALIGN")
            col.prop(scene, 'bias', slider=True)

        elif scene.algorithm == 'ELLERS':
            col.prop(scene, 'bias', slider=True)

        box.prop(scene, 'use_list_maze', text="Generate Maze From List")
        if scene.use_list_maze:
            box.prop_search(scene, 'list_maze', bpy.data, 'texts', text="List Maze")

        # write list maze box
        box = layout.box()
        box.prop(scene, 'write_list_maze', text="Write Maze List")


class ImageConverterPanelMG(Panel):
    bl_label = "Image Converter [PRO]"
    bl_idname = "3D_VIEW_PT_layout_ImageConverter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # image box
        box = layout.box()
        row = box.row()
        row.label("(X: {}, Y: {})".format(scene.mg_width, scene.mg_height))
        box.operator("maze_gen.convert_maze_image", icon="TEXT")
        box.prop_search(scene, 'maze_image', bpy.data, "images", "Image Maze")

        box.operator("maze_gen.create_image_from_list", icon="IMAGE_COL")
        box.prop_search(scene, 'list_maze', bpy.data, "texts", "List Maze")


class MazeTilesPanelMG(Panel):
    bl_label = "Maze Tiles [PRO]"
    bl_idname = "3D_VIEW_PT_layout_MazeTiles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # modeled tiles box
        box = layout.box()
        box.prop(scene, 'tile_based', text="Use Modeled Tiles")
        if scene.tile_based:
            row = box.row()
            row.prop(scene, 'tile_mode', expand=True)

            # generate demo tiles
            sub_box = box.box()
            sub_box.menu('maze_gen.tile_import_menu', text="Import Tile Set")

            sub_box = box.box()
            sub_box.prop(scene, 'merge_objects', text="Merge Objects")
            if scene.merge_objects:
                sub_box.prop(scene, 'apply_modifiers', text="Apply Modifiers")
                sub_box.prop(scene, 'remove_doubles_merge', text="Remove Doubles")

            row = layout.row()
            row.separator()

            box = layout.box()
            box.label("Tiles", icon='MESH_GRID')
            # list of tiles types needed
            col = box.column()
            if scene.tile_mode == "TWELVE_TILES":
                col.label("Wall Pieces:")
                col.prop_search(scene, 'wall_4_sided', bpy.data, "objects", "4 Sided Wall")
                col.prop_search(scene, 'wall_3_sided', bpy.data, "objects", "3 Sided Wall")
                col.prop_search(scene, 'wall_2_sided', bpy.data, "objects", "2 Sided Wall")
                col.prop_search(scene, 'wall_1_sided', bpy.data, "objects", "1 Sided Wall")
                col.prop_search(scene, 'wall_0_sided', bpy.data, "objects", "0 Sided Wall")
                col.prop_search(scene, 'wall_corner', bpy.data, "objects", "Wall Corner")
                col = box.column()
                col.label("Floor Pieces:")
                col.prop_search(scene, 'floor_4_sided', bpy.data, "objects", "4 Sided Floor")
                col.prop_search(scene, 'floor_3_sided', bpy.data, "objects", "3 Sided Floor")
                col.prop_search(scene, 'floor_2_sided', bpy.data, "objects", "2 Sided Floor")
                col.prop_search(scene, 'floor_1_sided', bpy.data, "objects", "1 Sided Floor")
                col.prop_search(scene, 'floor_0_sided', bpy.data, "objects", "0 Sided Floor")
                col.prop_search(scene, 'floor_corner', bpy.data, "objects", "Floor Corner")
            elif scene.tile_mode == "SIX_TILES":
                col.label("Pieces:")
                col.prop_search(scene, 'four_way', bpy.data, "objects", "4-Way")
                col.prop_search(scene, 't_int', bpy.data, "objects", "3-Way")
                col.prop_search(scene, 'turn', bpy.data, "objects", "Turn")
                col.prop_search(scene, 'dead_end', bpy.data, "objects", "Dead End")
                col.prop_search(scene, 'straight', bpy.data, "objects", "Straight Path")
                col.prop_search(scene, 'no_path', bpy.data, "objects", "Wall Only")


class BatchGeneratorPanelMG(Panel):
    bl_label = "Batch Gen [PRO]"
    bl_idname = "3D_VIEW_PT_layout_BatchGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("maze_gen.batch_generate_maze", icon="PACKAGE")
        box.operator("maze_gen.store_batch_maze", icon="FILE")

        row = box.row(align=True)
        row.operator("maze_gen.refresh_batch_num", icon="LOAD_FACTORY")
        sub_col = row.column()
        sub_col.enabled = False
        sub_col.prop(scene, 'num_batch_mazes', text="Batches")

        box.operator("maze_gen.clear_batch_maze", icon="CANCEL")

        row = layout.row()
        row.separator()

        box = layout.box()
        box.prop(scene, 'batch_index', text="Batch Index")
        box.operator("maze_gen.load_batch_maze", icon="OOPS")
        box.operator("maze_gen.delete_batch_maze", icon="X")


class InfoPanelMG(Panel):
    bl_label = "Info"
    bl_idname = "3D_VIEW_PT_layout_Info_mg"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.operator("maze_gen.show_workflows_image", icon="OOPS")
        box.operator("maze_gen.show_readme_text", icon="FILE_TEXT")

        row = layout.row()
        row.separator()

        # time settings box
        box = layout.box()
        box.label("Time Estimate", icon="TIME")
        col = box.column()
        col.operator("maze_gen.estimate_time_mg", icon="QUESTION")


class HelpPanelMG(Panel):
    bl_label = "Help"
    bl_idname = "3D_VIEW_PT_layout_Help_mg"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.label("What do you want?")
        row = box.row()
        row.prop(scene, 'generation_desire', text="")

        row = box.row()
        row.label("What do you have?")
        row = box.row()
        row.prop(scene, 'user_provision', text="")

        box = layout.box()
        if scene.generation_desire == "SIMP_3D" and scene.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from list")
            row = box.row()
            row.label("2. Hit Generate Maze")

        elif scene.generation_desire == "SIMP_3D" and scene.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Select image in image converter")
            row = box.row()
            row.label("2. Hit convert to text")
            row = box.row()
            row.label("3. Enable Gen from list")
            row = box.row()
            row.label("4. Select text block")
            row = box.row()
            row.label("5. Hit Generate Maze")

        elif scene.generation_desire == "SIMP_3D" and scene.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Enable Gen from list")
            row = box.row()
            row.label("2. Select text block")
            row = box.row()
            row.label("3. Hit Generate Maze")

        elif scene.generation_desire == "TILE_MAZE" and scene.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from list")
            row = box.row()
            row.label("2. Enable Use Modeled tiles")
            row = box.row()
            row.label("3. Assign appropriate tiles")
            row = box.row()
            row.label("4. Hit Generate Maze")

        elif scene.generation_desire == "TILE_MAZE" and scene.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Select image in image converter")
            row = box.row()
            row.label("2. Hit convert to text")
            row = box.row()
            row.label("3. Enable Gen from list")
            row = box.row()
            row.label("4. Select text block")
            row = box.row()
            row.label("5. Enable Use Modeled tiles")
            row = box.row()
            row.label("6. Assign appropriate tiles")
            row = box.row()
            row.label("7. Hit Generate Maze")

        elif scene.generation_desire == "TILE_MAZE" and scene.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Enable Gen from list")
            row = box.row()
            row.label("2. Select text block")
            row = box.row()
            row.label("3. Enable Use Modeled tiles")
            row = box.row()
            row.label("4. Assign appropriate tiles")
            row = box.row()
            row.label("5. Hit Generate Maze")

        elif scene.generation_desire == "TEXT_MAZE" and scene.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from List")
            row = box.row()
            row.label("2. Enable write maze list")
            row = box.row()
            row.label("3. Hit Generate Maze")

        elif scene.generation_desire == "TEXT_MAZE" and scene.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Select image in image converter")
            row = box.row()
            row.label("2. Hit convert to text")

        elif scene.generation_desire == "TEXT_MAZE" and scene.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Already done!")

        elif scene.generation_desire == "IMAGE_MAZE" and scene.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Enable write maze list")
            row = box.row()
            row.label("2. Disable Gen 3D maze")
            row = box.row()
            row.label("3. Hit Generate Maze")
            row = box.row()
            row.label("4. Select text in image converter")
            row = box.row()
            row.label("5. Hit convert to image")

        elif scene.generation_desire == "IMAGE_MAZE" and scene.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Already done!")

        elif scene.generation_desire == "IMAGE_MAZE" and scene.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Select text in image converter")
            row = box.row()
            row.label("2. Hit convert to image")


class MazeAddonPrefsMg(AddonPreferences):
    bl_idname = __name__

    open_help_outbldr = BoolProperty(
        name="open_help_outbldr",
        default=True,
        description="Open help files outside of Blender instead of in Blender's text editor and image editor. Will open all help files as if you double clicked them in an explorer window (only available on Windows)."
    )

    debug_mode = BoolProperty(
        name="debug_mode",
        default=False,
        description="Only for development! Do not touch!")

    use_custom_tile_path = BoolProperty(
        name="use_custom_tile_path",
        default=False,
        description="Use custom tile path")

    custom_tile_path = StringProperty(
        name="custom_tile_path",
        default=os.getcwd(),
        description="Custom tile path",
        subtype='FILE_PATH')

    always_save_prior = BoolProperty(
        name="always_save_prior",
        default=True,
        description="Always save .blend file before executing" +
                    "time-consuming operations")

    save_all_images = BoolProperty(
        name="save_all_images",
        default=True,
        description="Always save images before executing" +
                    "time-consuming operations")

    save_all_texts = BoolProperty(
        name="save_all_texts",
        default=True,
        description="Always save texts before executing" +
                    "time-consuming operations")

    show_quickhelp = BoolProperty(
        name="Quick Help",
        default=False,
        description="Show quick help")

    only_odd_sizes = BoolProperty(
        name="Only Odd Maze Sizes",
        default=True,
        description="Convert all even sizes to odd upon generation"
    )

    show_advanced_settings = BoolProperty(
        name="Show Advanced Settings",
        default=False,
        description="WARNING: Only for advanced users! Don't go in here!"
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = col.row()
        row.prop(self, 'open_help_outbldr', text="Open Help Outside Blender")
        col.row()
        box = col.box()
        box.prop(self, 'use_custom_tile_path', text="Use Custom Path")
        row = box.row()
        row.prop(self, 'custom_tile_path', text="")
        col.row()
        col.prop(self, 'always_save_prior', text="Save .blend File")
        col = layout.row()
        col.prop(self, 'save_all_images', text="Save Images")
        col = layout.row()
        col.prop(self, 'save_all_texts', text="Save Texts")

        layout.row()
        # quick help box
        box = layout.box()
        row = box.row()
        row.prop(self, "show_quickhelp", toggle=True)
        if self.show_quickhelp:
            box.row()
            row = box.row()
            row.scale_y = 0.5
            row.label(text="If Blender locks up where you have unsaved work " + "and you are fortunate enough to have found this do not")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="close Blender . . . yet. Read this first and/or " + "contact support, if needed, to try to salvage your progress.")
            box.row()
            row = box.row()
            row.scale_y = 0.5
            row.label(text="The amount of time for most maze operations to " + "complete will increase exponentially with the size " + "of the maze.")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="Blender freezes its UI when scripts are " + "executing, however, this can be combated with a few " + "tricks as follows")
            # blank row for paragraph
            box.row()
            row = box.row()
            row.scale_y = 0.5
            row.label(text="First, open a system console window (for " + "Windows available from Info Header > Window > Toggle " + "System Console)")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="to see progress as a percent or to stop the " + "operation (with Ctrl-C). It is important to have this open " + "before")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="starting an operation, because it can't easily " + "be opened after you start an operator " + "(by pressing any UI button).")
            box.row()
            row = box.row()
            row.scale_y = 0.5
            row.label(text="Another useful tip is to always save your work " + "before generating anything or use a blank " + ".blend file for generation.")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="This will allow you to force Blender to close " + "without losing your work. This can be done automatically " + "by leaving the")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="3 checkboxes above (Save .blend File, " + "Save Images . . . ) enabled.")

        layout.row()

        row = layout.row()
        row.label(text="Support:")
        row = layout.row()
        row.scale_y = 0.5
        row.label(text="Please contact support if you have any problems.")

        layout.row()

        row = layout.row()
        row.scale_y = 1
        # website url
        row.operator("wm.url_open", text="Support Website", icon='QUESTION').url = "http://integrity-sg.com"
        # e-mail
        row.operator("wm.url_open", text="Support E-Mail", icon='LINENUMBERS_ON').url = "mailto: assetsupport@integrity-sg.com"

        layout.row()

        box = layout.box()
        row = box.row()
        row.prop(self, "show_advanced_settings", toggle=True)
        if self.show_advanced_settings:
            row = box.row()
            row.prop(self, 'only_odd_sizes')
            row.prop(self, 'debug_mode', text="Debug")

# Text Editor
class MazeGeneratorTextToolsPanelMG(Panel):
    bl_label = "Maze Generator Tools"
    bl_idname = "TEXT_EDITOR_PT_layout_MazeGenerator"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop_search(scene, 'list_maze', bpy.data, 'texts', text="List Maze")

        box = layout.box()
        box.operator("maze_gen.invert_text_mg", icon="ARROW_LEFTRIGHT")

        box = layout.box()
        box.operator("maze_gen.replace_text_mg", icon="FONT_DATA")
        box.prop(scene, 'text1_mg', text="Find")
        box.prop(scene, 'text2_mg', text="Replace")


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


class ShowHelpDiagramMG(Operator):
    bl_label = "Workflows Diagram"
    bl_idname = "maze_gen.show_workflows_image"
    bl_description = "Shows a workflow diagram in the image editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_prefs = context.user_preferences.addons['maze_gen'].preferences

        my_directory = os.path.join(os.path.dirname(__file__), "help")
        image_filepath = os.path.join(my_directory, "Workflow Diagram.png")

        if not addon_prefs.open_help_outbldr:
            bpy.ops.image.open(filepath=image_filepath,
                               directory=my_directory,
                               files=[{"name": "Workflow Diagram.png"}],
                               relative_path=True,
                               show_multiview=False)
            self.report({'INFO'}, "See workflow diagram in the image editor")
        else:
            open_file(image_filepath)

        return {'FINISHED'}


class ShowReadmeMG(Operator):
    bl_label = "Readme"
    bl_idname = "maze_gen.show_readme_text"
    bl_description = "Shows readme in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_prefs = context.user_preferences.addons['maze_gen'].preferences

        my_directory = os.path.join(os.path.dirname(__file__), "help")
        my_filepath = os.path.join(my_directory, "Readme.txt")

        if not addon_prefs.open_help_outbldr:
            bpy.ops.text.open(filepath=my_filepath)  # TODO - Open in new blender window with readme
            self.report({'INFO'}, "See readme in the text editor")
        else:
            open_file(my_filepath)
        
        return {'FINISHED'}


# demo tile objects generation
class DemoTilesImportMG(Operator):
    bl_label = "Generate Tiles"
    bl_idname = "maze_gen.import_tileset"
    bl_description = "Imports tiles."
    bl_options = {'UNDO'}

    filename = StringProperty(name="File Name")

    def execute(self, context):
        addon_prefs = context.user_preferences.addons['maze_gen'].preferences

        my_tiles_dir = os.path.join(os.path.dirname(__file__), "tiles")
        my_filepath = os.path.join(my_tiles_dir, self.filename)
        if not os.access(my_filepath, os.R_OK) and addon_prefs.use_custom_tile_path:
            my_filepath = os.path.join(
                addon_prefs.custom_tile_path,
                self.filename)
            if not os.access(my_filepath, os.R_OK):
                self.report({'ERROR'}, "The selected tile set could not be imported! Most likely your custom tile path is not set to a valid path.")
                return {'CANCELLED'}

        append_objs(my_filepath)

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


class EnableLayerMG(Operator):
    bl_label = "Enable First Layer"
    bl_idname = "maze_gen.enable_layer"
    bl_description = "Enables first layer so UltiMaze can work :)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.layers[0] = True
        return {'FINISHED'}


# main maze gen controller
class GenerateMazeMG(Operator):
    bl_label = "Generate Maze"
    bl_idname = "maze_gen.generate_maze"
    bl_description = "Generates a 3D maze"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene

        if not scene.layers[0]:
            bpy.ops.wm.call_menu(name=menus.EnableLayerMenu.bl_idname)
            return {'CANCELLED'}

        messages, message_lvls, status = maze_gen.make_maze(context)
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)

        return {status}


# classes to register
classes = [MazeAddonPrefsMg,
           # Main
           GenerateMazeMG,
           DemoTilesImportMG,
           ShowHelpDiagramMG,
           ShowReadmeMG,
           # Batch Generation
           batch_gen.BatchGenerateMazeMG,
           batch_gen.StoreBatchMazeMG,
           batch_gen.ClearBatchMazesMG,
           batch_gen.RefreshBatchMazesMG,
           batch_gen.LoadBatchMazeMG,
           batch_gen.DeleteBatchMazeMG,
           # Time Log
           time_log.EstimateTimeMG,
           # UI Panels
           MazeGeneratorPanelMG,
           ImageConverterPanelMG,
           MazeTilesPanelMG,
           BatchGeneratorPanelMG,
           InfoPanelMG,
           HelpPanelMG,
           MazeGeneratorTextToolsPanelMG,
           # Text Tools
           text_tools.ReplaceTextMG,
           text_tools.InvertTextMG,
           # Text/Image Conversion
           txt_img_converter.ConvertMazeImageMG,
           txt_img_converter.CreateImageFromListMG,
           # Specials
           EnableLayerMG,
           # Menus
           menus.TileImportMenu,
           menus.EnableLayerMenu,
           menus.SaveUserPrefsMenu]

# ================== REGISTRY TABLE OF CONTENTS ===================
#
# ---------------------- General Settings -------------------------
# --------------------------- Tiles -------------------------------
# ----------------------- Tile Settings ---------------------------
# ----------------------- List Settings ---------------------------
# ------------------------ Loop Adding ----------------------------
# -------------------- Algorithm Settings -------------------------
# ----------------------- Batch Tools -----------------------------
# -------------------- Text Find/Replace --------------------------
# ------------------------ Image Maze -----------------------------
# ------------------------ Help Enums -----------------------------


def register():
    for i in classes:
        print(i)
        register_class(i)

    # ---------------------- General Settings -------------------------

    Scene.mg_width = IntProperty(
        name="Width", default=25, min=3, max=999)

    Scene.mg_height = IntProperty(
        name="Height", default=25, min=3, max=999)

    Scene.gen_3d_maze = BoolProperty(
        name="gen_3d_maze",
        default=True)

    # --------------------------- Tiles -------------------------------

    Scene.wall_4_sided = StringProperty(
        name="wall_4_sided",
        default="wall_4_sided",
        description="Wall piece with 4 sides")

    Scene.wall_3_sided = StringProperty(
        name="wall_3_sided",
        default="wall_3_sided",
        description="Wall piece with 3 sides")

    Scene.wall_2_sided = StringProperty(
        name="wall_2_sided",
        default="wall_2_sided",
        description="Wall piece with 2 opposite sides")

    Scene.wall_1_sided = StringProperty(
        name="wall_1_sided",
        default="wall_1_sided",
        description="Wall piece with 1 side")

    Scene.wall_0_sided = StringProperty(
        name="wall_0_sided",
        default="wall_0_sided",
        description="Wall piece with 0 sides")

    Scene.wall_corner = StringProperty(
        name="wall_corner",
        default="wall_corner",
        description="Wall piece with 2 adjacent sides")

    Scene.floor_4_sided = StringProperty(
        name="floor_4_sided",
        default="floor_4_sided",
        description="Floor piece with 4 sides")

    Scene.floor_3_sided = StringProperty(
        name="floor_3_sided",
        default="floor_3_sided",
        description="Floor piece with 3 sides")

    Scene.floor_2_sided = StringProperty(
        name="floor_2_sided",
        default="floor_2_sided",
        description="Floor piece with 2 opposite sides")

    Scene.floor_1_sided = StringProperty(
        name="floor_1_sided",
        default="floor_1_sided",
        description="Floor piece with 1 side")

    Scene.floor_0_sided = StringProperty(
        name="floor_0_sided",
        default="floor_0_sided",
        description="Floor piece with 0 sides")

    Scene.floor_corner = StringProperty(
        name="floor_corner",
        default="floor_corner",
        description="Floor piece with 2 adjacent sides")

    Scene.four_way = StringProperty(
        name="four_way",
        default="four_way",
        description="4-way (+) intersection")

    Scene.t_int = StringProperty(
        name="t_int",
        default="t_int",
        description="3-way (T) intersection")

    Scene.turn = StringProperty(
        name="turn",
        default="turn",
        description="2-way (L) intersection")

    Scene.dead_end = StringProperty(
        name="dead_end",
        default="dead_end",
        description="Dead-end (]) tile")

    Scene.straight = StringProperty(
        name="straight",
        default="straight",
        description="Straight (|) tile")

    Scene.no_path = StringProperty(
        name="no_path",
        default="no_path",
        description="Wall-only (0) tile")

    # ----------------------- Tile Settings ---------------------------

    Scene.tile_based = BoolProperty(
        name="tile_based", default=False)

    Scene.tile_mode = EnumProperty(
        items=[('TWELVE_TILES', "12-Piece Mode", "Use 12 tile pieces."),
               ('SIX_TILES', "6-Piece Mode", "Use 6 tile pieces.")],
        name="Tile Mode",
        description="Number of tiles to use.",
        default="TWELVE_TILES")

    Scene.import_mat = BoolProperty(
        name="import_mat",
        default=True)

    Scene.merge_objects = BoolProperty(
        name="merge_objects",
        default=True)

    Scene.remove_doubles_merge = BoolProperty(
        name="remove_doubles_merge",
        default=True)

    Scene.apply_modifiers = BoolProperty(
        name="apply_modifiers",
        default=True)

    # ----------------------- List Settings ---------------------------

    Scene.list_maze = StringProperty(
        name="list_maze",
        default="")

    Scene.use_list_maze = BoolProperty(
        name="use_list_maze",
        default=False,
        description="Generate maze from 1s and 0s from text data block")

    Scene.write_list_maze = BoolProperty(
        name="write_list_maze",
        default=False)

    # ------------------------ Loop Adding ----------------------------

    Scene.allow_loops = BoolProperty(
        name="allow_loops",
        default=False)

    Scene.loops_chance = IntProperty(
        name="loops_chance",
        default=3,
        min=1,
        max=1000000,
        description="1/x chance of creating each possible loop")

    # -------------------- Algorithm Settings -------------------------

    Scene.algorithm = EnumProperty(
        items=[('DEPTH_FIRST', "Depth-First", ""),
               ('BREADTH_FIRST', "Breadth-First", ""),
               ('PRIMS', "Prim's", ""),
               ('BINARY_TREE', "Binary Tree", ""),
               ('KRUSKALS', "Kruskal's", ""),
               ('ELLERS', "Eller's", "")],
        name="Algorithm",
        description="Algorithm to use when generating maze paths internally",
        default="DEPTH_FIRST")

    Scene.binary_dir = EnumProperty(
        items=[('RANDOM', "Random", ""),
               ('NE', "North-East", ""),
               ('NW', "North-West", ""),
               ('SE', "South-East", ""),
               ('SW', "South-West", "")],
        name="Binary Tree Direction",
        description="Bias diagonal for binary tree maze algorithm",
        default="RANDOM")

    Scene.tileable = BoolProperty(
        name="Tileable",
        description="Makes resulting maze tileable",
        default=True)

    Scene.bias_direction = EnumProperty(
        items=[('RANDOM', "Random", ""),
               ('X', "X-Axis", ""),
               ('Y', "Y-Axis", "")],
        name="Bias Direction",
        description="Bias direction for graph theory based algorithms",
        default="RANDOM")

    Scene.bias = FloatProperty(
        name="Bias",
        description="Amount of bias for graph theory based algorithms:\n    0 = no bias\n    1 = high bias",
        default=0,
        min=0,
        max=1)

    # ----------------------- Batch Tools -----------------------------

    Scene.num_batch_mazes = IntProperty(
        name="num_batch_mazes",
        default=0,
        min=0,
        max=1000000,
        description="Number of mazes to batch generate")

    Scene.batch_index = IntProperty(
        name="batch_index",
        default=1,
        min=1,
        max=1000000,
        description="Batch index to load stored setting")

    # -------------------- Text Find/Replace --------------------------

    Scene.text1_mg = StringProperty(
        name="text1_mg",
        default="")

    Scene.text2_mg = StringProperty(
        name="text2_mg",
        default="")

    # ------------------------ Image Maze -----------------------------

    Scene.maze_image = StringProperty(
        name="maze_image",
        default="")

    # ------------------------ Help Enums -----------------------------

    Scene.generation_desire = EnumProperty(
        items=[('SIMP_3D', "Simple 3D Maze", ""),
               ('TILE_MAZE', "Tile Maze", ""),
               ('TEXT_MAZE', "Text Maze", ""),
               ('IMAGE_MAZE', "Image Maze", "")],
        name="Desired",
        description="What would you like to have?",
        default="SIMP_3D")

    Scene.user_provision = EnumProperty(
        items=[('SETTINGS', "Layout Settings", ""),
               ('IMAGE_MAZE', "Image Maze", ""),
               ('TEXT_MAZE', "Text Maze", "")],
        name="You Have",
        description="What do you have?",
        default="SETTINGS")


def unregister():
    for i in classes:
        unregister_class(i)

    # ---------------------- General Settings -------------------------

    del Scene.mg_width
    del Scene.mg_height
    del Scene.gen_3d_maze

    # --------------------------- Tiles -------------------------------

    del Scene.wall_4_sided
    del Scene.wall_3_sided
    del Scene.wall_2_sided
    del Scene.wall_1_sided
    del Scene.wall_0_sided
    del Scene.wall_corner

    del Scene.floor_4_sided
    del Scene.floor_3_sided
    del Scene.floor_2_sided
    del Scene.floor_1_sided
    del Scene.floor_0_sided
    del Scene.floor_corner

    del Scene.four_way
    del Scene.t_int
    del Scene.turn
    del Scene.straight
    del Scene.dead_end
    del Scene.no_path

    # ----------------------- Tile Settings ---------------------------

    del Scene.tile_based
    del Scene.tile_mode
    del Scene.import_mat
    del Scene.merge_objects
    del Scene.apply_modifiers
    del Scene.remove_doubles_merge

    # ----------------------- List Settings ---------------------------

    del Scene.list_maze
    del Scene.use_list_maze
    del Scene.write_list_maze

    # ------------------------ Loop Adding ----------------------------

    del Scene.allow_loops
    del Scene.loops_chance

    # -------------------- Algorithm Settings -------------------------

    del Scene.algorithm
    del Scene.binary_dir
    del Scene.tileable
    del Scene.bias_direction
    del Scene.bias

    # ----------------------- Batch Tools -----------------------------

    del Scene.num_batch_mazes
    del Scene.batch_index

    # -------------------- Text Find/Replace --------------------------

    del Scene.text1_mg
    del Scene.text2_mg

    # ------------------------ Image Maze -----------------------------

    del Scene.maze_image

    # ------------------------ Help Enums -----------------------------

    del Scene.generation_desire
    del Scene.user_provision


if __name__ == "__main__":
    register()
