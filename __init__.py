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

"""
===== MAZE GENERATOR [PRO] V.2.3.4 =====
This __init__ module handles some UI and also registers all
classes and properties.
"""
import os
import sys
import subprocess
from os.path import basename, dirname

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, Scene, AddonPreferences, PropertyGroup
from bpy.utils import register_class, unregister_class, previews

from . import maze_gen
from . import batch_gen
from . import text_tools
from . import time_log
from . import txt_img_converter
from . import menus
from . import render_kit
from . import utils
from .logging_setup import setup_logger
from . import ascii_logo
from .addon_name import save_addon_name, get_addon_name
from . import addon_updater_ops
from . import bug_reporter

logger = setup_logger(__name__)

bl_info = {
    "name": "UltiMaze [PRO]",
    "author": "Jake Dube",
    "version": (2, 3, 4),
    "blender": (2, 76, 0),
    "location": "3D View > Tools > Maze Gen",
    "description": "Generates 3-dimensional mazes.",
    "warning": "May take a long time to generate maze: "
               "see quick help below.",
    "wiki_url": "",
    "tracker_url": "https://github.com/ekaj2/UltiMaze/issues",
    "category": "3D View",
    "support": "COMMUNITY",
}

setup_logger(__name__)


def clear_preview_collections(pcs):
    # clear everything out
    for pcoll in pcs.values():
        previews.remove(pcoll)
    pcs.clear()


def set_main_pcoll(pcs):
    pcoll = previews.new()
    pcoll.previews_dir = ""
    pcoll.previews = ()
    pcoll.tile_mode = ""
    pcoll.scan = False  # this is used to force a directory scan
    pcs["main"] = pcoll


def enum_previews_from_directory(self, context):
    """EnumProperty callback for building a list of enum items"""
    addon_prefs = context.user_preferences.addons[get_addon_name()].preferences

    logger.debug("beginning to build the enum_previews_from_directory")

    enum_items = []
    mg = context.scene.mg

    # return an empty list if there is no context
    if context is None:
        logger.warning("in enum_previews_from_directory...context is None...this is potentially normal")
        return enum_items

    # get the preview collection...defined in register()
    pcoll = preview_collections["main"]

    # if the pcoll directory is the same as the one specified in the UI, do nothing to change the list
    if addon_prefs.tiles_path == pcoll.previews_dir and pcoll.tile_mode == mg.tile_mode and not pcoll.scan:
        logger.debug("not doing anything...returning pcoll.previews without modifications")
        return pcoll.previews

    # otherwise, begin scanning the directory
    logger.debug("Scanning directory:{}".format(addon_prefs.tiles_path))

    clear_preview_collections(preview_collections)
    set_main_pcoll(preview_collections)

    if addon_prefs.tiles_path and os.path.exists(addon_prefs.tiles_path):
        # scan the directory for png files
        i = 0
        filenames = os.listdir(addon_prefs.tiles_path)
        for filename in filenames:
            # this would be changing "demo.png" to "demo"
            name = filename[:-4]
            if filename.lower().endswith(".png") and any([a == name + ".blend" for a in filenames]):
                # skip anything without 2 ending for 12 tiles, anything without 6 ending for 6 tiles
                if mg.tile_mode == "TWELVE_TILES" and not name.endswith("2"):
                    continue
                elif mg.tile_mode == "SIX_TILES" and not name.endswith("6"):
                    continue

                # generates a thumbnail preview for a file
                filepath = os.path.join(addon_prefs.tiles_path, filename)
                logger.debug("loading the thumbnail:{}".format(filepath))
                thumb = pcoll.load(name, filepath, 'IMAGE')
                enum_items.append((name, name, "", thumb.icon_id, i))
                i += 1

    pcoll.previews = enum_items
    pcoll.previews_dir = addon_prefs.tiles_path
    pcoll.tile_mode = mg.tile_mode
    pcoll.scan = False
    logger.debug("Returning pcoll.previews")
    return pcoll.previews


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
        addon_updater_ops.check_for_update_background(context)

        scene = context.scene
        mg = scene.mg
        layout = self.layout

        # Generate Maze button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("maze_gen.generate_maze", icon="MOD_BUILD")

        # layout settings box
        box = layout.box()
        box.label("Layout Settings", icon='SETTINGS')
        box.prop(mg, 'mg_width', slider=False, text="Width")
        box.prop(mg, 'mg_height', slider=False, text="Height")
        box.prop(mg, 'gen_3d_maze', text="Generate 3D Maze")

        col = box.box()

        if mg.use_list_maze:
            col.enabled = False
        else:
            col.enabled = True
        row = col.row()
        row.prop(mg, 'allow_loops', text="Allow Loops")
        row.prop(mg, 'loops_chance', text="Chance")

        col.prop(mg, 'algorithm', text="", icon="OOPS")
        if mg.algorithm == 'BINARY_TREE':
            col.prop(mg, 'binary_dir', text="", icon="MOD_DECIM")
            col.prop(mg, 'tileable')

        elif mg.algorithm in ['PRIMS', 'DEPTH_FIRST', 'BREADTH_FIRST']:
            col.prop(mg, 'bias_direction', text="", icon="ALIGN")
            col.prop(mg, 'bias', slider=True)

        elif mg.algorithm == 'ELLERS':
            col.prop(mg, 'bias', slider=True)

        box.prop(mg, 'use_list_maze', text="Generate Maze From List")
        if mg.use_list_maze:
            box.prop_search(mg, 'list_maze', bpy.data, 'texts', text="List Maze")

        # write list maze box
        box = layout.box()
        box.prop(mg, 'write_list_maze', text="Write Maze List")

        addon_updater_ops.update_notice_box_ui(self, context)


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
        mg = scene.mg
        layout = self.layout

        # image box
        box = layout.box()
        row = box.row()
        row.label("(X: {}, Y: {})".format(mg.mg_width, mg.mg_height))
        box.operator("maze_gen.convert_maze_image", icon="TEXT")
        box.prop_search(mg, 'maze_image', bpy.data, "images", "Image Maze")

        box.operator("maze_gen.create_image_from_list", icon="IMAGE_COL")
        box.prop_search(mg, 'list_maze', bpy.data, "texts", "List Maze")


class MazeTilesPanelMG(Panel):
    bl_label = "Maze Tiles [PRO]"
    bl_idname = "3D_VIEW_PT_layout_MazeTiles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        addon_prefs = context.user_preferences.addons[get_addon_name()].preferences
        scene = context.scene
        mg = scene.mg
        layout = self.layout

        # modeled tiles box
        box = layout.box()
        box.prop(mg, 'tile_based', text="Use Modeled Tiles")
        if mg.tile_based:
            row = box.row()
            row.prop(mg, 'tile_mode', expand=True)

            # generate demo tiles
            sub_box = box.box()

            if mg.tile_importer:
                sub_box.prop(mg, 'tile_importer', toggle=True, icon='TRIA_DOWN')

                sub_box.label("Select Tileset:")
                col = sub_box.column(align=True)
                if addon_prefs.use_large_menus:
                    col.template_icon_view(mg, 'tiles', addon_prefs.show_icon_name, addon_prefs.icon_scale)
                else:
                    col.prop(mg, 'tiles', text="")

                row = sub_box.row()
                row.scale_y = 1.5
                row.operator('maze_gen.import_tileset', icon='UV_FACESEL')
            else:
                sub_box.prop(mg, 'tile_importer', toggle=True, icon='TRIA_RIGHT')

            sub_box = box.box()
            sub_box.prop(mg, 'apply_modifiers', text="Apply Modifiers")
            sub_box.prop(mg, 'merge_objects', text="Merge Objects")
            if mg.merge_objects:
                sub_box.prop(mg, 'remove_doubles_merge', text="Remove Doubles")

            row = layout.row()
            row.separator()

            box = layout.box()
            box.label("Tiles", icon='MESH_GRID')
            # list of tiles types needed
            col = box.column()
            if mg.tile_mode == "TWELVE_TILES":
                col.label("Wall Pieces:")
                col.prop_search(mg, 'wall_4_sided', bpy.data, "objects", "4 Sided Wall")
                col.prop_search(mg, 'wall_3_sided', bpy.data, "objects", "3 Sided Wall")
                col.prop_search(mg, 'wall_2_sided', bpy.data, "objects", "2 Sided Wall")
                col.prop_search(mg, 'wall_1_sided', bpy.data, "objects", "1 Sided Wall")
                col.prop_search(mg, 'wall_0_sided', bpy.data, "objects", "0 Sided Wall")
                col.prop_search(mg, 'wall_corner', bpy.data, "objects", "Wall Corner")
                col = box.column()
                col.label("Floor Pieces:")
                col.prop_search(mg, 'floor_4_sided', bpy.data, "objects", "4 Sided Floor")
                col.prop_search(mg, 'floor_3_sided', bpy.data, "objects", "3 Sided Floor")
                col.prop_search(mg, 'floor_2_sided', bpy.data, "objects", "2 Sided Floor")
                col.prop_search(mg, 'floor_1_sided', bpy.data, "objects", "1 Sided Floor")
                col.prop_search(mg, 'floor_0_sided', bpy.data, "objects", "0 Sided Floor")
                col.prop_search(mg, 'floor_corner', bpy.data, "objects", "Floor Corner")
            elif mg.tile_mode == "SIX_TILES":
                col.label("Pieces:")
                col.prop_search(mg, 'four_way', bpy.data, "objects", "4-Way")
                col.prop_search(mg, 't_int', bpy.data, "objects", "3-Way")
                col.prop_search(mg, 'turn', bpy.data, "objects", "Turn")
                col.prop_search(mg, 'dead_end', bpy.data, "objects", "Dead End")
                col.prop_search(mg, 'straight', bpy.data, "objects", "Straight Path")
                col.prop_search(mg, 'no_path', bpy.data, "objects", "Wall Only")


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
        mg = scene.mg

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("maze_gen.batch_generate_maze", icon="PACKAGE")
        box.operator("maze_gen.store_batch_maze", icon="FILE")

        row = box.row(align=True)
        row.operator("maze_gen.refresh_batch_num", icon="LOAD_FACTORY")
        sub_col = row.column()
        sub_col.enabled = False
        sub_col.prop(mg, 'num_batch_mazes', text="Batches")

        box.operator("maze_gen.clear_batch_maze", icon="CANCEL")

        row = layout.row()
        row.separator()

        box = layout.box()
        box.prop(mg, 'batch_index', text="Batch Index")
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

        box = layout.box()
        box.scale_y = 2
        box.operator('maze_gen.report_bug', icon="HELP")


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
        mg = scene.mg
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.label("What do you want?")
        row = box.row()
        row.prop(mg, 'generation_desire', text="")

        row = box.row()
        row.label("What do you have?")
        row = box.row()
        row.prop(mg, 'user_provision', text="")

        box = layout.box()
        if mg.generation_desire == "SIMP_3D" and mg.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from list")
            row = box.row()
            row.label("2. Hit Generate Maze")

        elif mg.generation_desire == "SIMP_3D" and mg.user_provision == "IMAGE_MAZE":
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

        elif mg.generation_desire == "SIMP_3D" and mg.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Enable Gen from list")
            row = box.row()
            row.label("2. Select text block")
            row = box.row()
            row.label("3. Hit Generate Maze")

        elif mg.generation_desire == "TILE_MAZE" and mg.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from list")
            row = box.row()
            row.label("2. Enable Use Modeled tiles")
            row = box.row()
            row.label("3. Assign appropriate tiles")
            row = box.row()
            row.label("4. Hit Generate Maze")

        elif mg.generation_desire == "TILE_MAZE" and mg.user_provision == "IMAGE_MAZE":
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

        elif mg.generation_desire == "TILE_MAZE" and mg.user_provision == "TEXT_MAZE":
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

        elif mg.generation_desire == "TEXT_MAZE" and mg.user_provision == "SETTINGS":
            row = box.row()
            row.label("1. Disable Gen Maze from List")
            row = box.row()
            row.label("2. Enable write maze list")
            row = box.row()
            row.label("3. Hit Generate Maze")

        elif mg.generation_desire == "TEXT_MAZE" and mg.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Select image in image converter")
            row = box.row()
            row.label("2. Hit convert to text")

        elif mg.generation_desire == "TEXT_MAZE" and mg.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Already done!")

        elif mg.generation_desire == "IMAGE_MAZE" and mg.user_provision == "SETTINGS":
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

        elif mg.generation_desire == "IMAGE_MAZE" and mg.user_provision == "IMAGE_MAZE":
            row = box.row()
            row.label("1. Already done!")

        elif mg.generation_desire == "IMAGE_MAZE" and mg.user_provision == "TEXT_MAZE":
            row = box.row()
            row.label("1. Select text in image converter")
            row = box.row()
            row.label("2. Hit convert to image")


class MazeAddonPrefsMg(AddonPreferences):
    bl_idname = basename(dirname(__file__))

    open_help_outbldr = BoolProperty(
        name="Open Help Outside Blender",
        default=True,
        description="Open help files outside of Blender instead of in Blender's text editor and image editor. Will "
                    "open all help files as if you double clicked them in an explorer window (only available "
                    "on Windows).")

    debug_mode = BoolProperty(
        name="debug_mode",
        default=False,
        description="Only for development! Do not touch!")

    always_save_prior = BoolProperty(
        name="Save .blend File",
        default=True,
        description="Always save .blend file before executing time-consuming operations")

    save_all_images = BoolProperty(
        name="Save Images",
        default=True,
        description="Always save images before executing time-consuming operations")

    save_all_texts = BoolProperty(
        name="Save Texts",
        default=True,
        description="Always save texts before executing time-consuming operations")

    show_quickhelp = BoolProperty(
        name="Quick Help",
        default=False,
        description="Show quick help")

    only_odd_sizes = BoolProperty(
        name="Only Odd Maze Sizes",
        default=True,
        description="Convert all even sizes to odd upon generation")

    show_advanced_settings = BoolProperty(
        name="Show Advanced Settings",
        default=False,
        description="WARNING: Only for advanced users! Don't go in here!")

    use_large_menus = BoolProperty(
        name="Use Large Menus Where Applicable",
        default=True,
        description="Some menus support loading large icons; enabling this will show this in the UI where possible.")

    show_icon_name = BoolProperty(name="Still Show Names In Menus", default=False)
    icon_scale = FloatProperty(name="Icon Size", min=1, max=10, default=5.0)

    tiles_path = StringProperty(
        name="Tiles Folder",
        subtype='DIR_PATH',
        default=os.path.join(os.path.dirname(__file__), "tiles"),
        update=lambda self, context: utils.make_absolute('tiles_path'))

    preview_samples = IntProperty(name="Samples", default=50, min=1, max=1000)

    # addon updater preferences
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )

    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 2
        row.operator('maze_gen.report_bug', icon="HELP")

        addon_updater_ops.update_settings_ui(self, context)

        layout.prop(self, 'open_help_outbldr')
        layout.separator()

        box = layout.box()
        box.prop(self, 'always_save_prior')
        box.prop(self, 'save_all_images')
        box.prop(self, 'save_all_texts')

        box = layout.box()
        box.prop(self, 'use_large_menus')
        if self.use_large_menus:
            box.prop(self, 'show_icon_name')
            box.prop(self, 'icon_scale', slider=True)

        col = box.column(align=True)
        col.prop(self, 'tiles_path', text="")
        row = col.row(align=True)
        row.operator('maze_gen.rescan_tiles_directory', icon='FILE_REFRESH', text="Force Rescan")
        row.operator('maze_gen.load_original_tiles', icon='LIBRARY_DATA_BROKEN', text="Load Original")
        row = col.row(align=True)
        row.menu('maze_gen.tile_render_menu')
        row.prop(self, 'preview_samples')

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
        mg = scene.mg

        row = layout.row()
        row.prop_search(mg, 'list_maze', bpy.data, 'texts', text="List Maze")

        box = layout.box()
        box.operator("maze_gen.invert_text_mg", icon="ARROW_LEFTRIGHT")

        box = layout.box()
        box.operator("maze_gen.replace_text_mg", icon="FONT_DATA")
        box.prop(mg, 'text1_mg', text="Find")
        box.prop(mg, 'text2_mg', text="Replace")


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
        addon_prefs = context.user_preferences.addons[get_addon_name()].preferences

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
        addon_prefs = context.user_preferences.addons[get_addon_name()].preferences

        readme_path = os.path.join(os.path.dirname(__file__), "help", "Readme.txt")
        if not addon_prefs.open_help_outbldr:
            bpy.ops.text.open(filepath=readme_path)
            self.report({'INFO'}, "See readme in the text editor")
        else:
            open_file(readme_path)
        
        return {'FINISHED'}


class RescanTilesPath(Operator):
    bl_label = "Reload (Scan) Tiles Path"
    bl_idname = "maze_gen.rescan_tiles_directory"
    bl_description = "Forces a scan on the tile path directory."

    def execute(self, context):
        preview_collections["main"].scan = True
        return {'FINISHED'}


class LoadOriginalTilesPath(Operator):
    bl_label = "Load Tiles Path"
    bl_idname = "maze_gen.load_original_tiles"
    bl_description = "Sets the tile path to the original add-on directory."
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        mg = context.scene.mg
        mg.tiles_path = os.path.join(os.path.dirname(__file__), "tiles")
        return {'FINISHED'}


# demo tile objects generation
class DemoTilesImportMG(Operator):
    bl_label = "Import Tileset"
    bl_idname = "maze_gen.import_tileset"
    bl_description = "Imports tiles."
    bl_options = {'UNDO'}

    def execute(self, context):
        addon_prefs = context.user_preferences.addons[get_addon_name()].preferences
        mg = context.scene.mg

        if not mg.tiles:
            self.report({'ERROR'}, "There are no available tiles. Please go to the user prefs "
                                   "\nto see if you are just missing the preview images. For tiles "
                                   "\nto show up here, there must be a .blend file and a .png file "
                                   "\nwith the same name other than the file extension. Once you "
                                   "\nhave built a tileset (the .blend file), you can use the tool "
                                   "\nin the add-on preferences for UltiMaze to automatically render "
                                   "\nout and save a nice preview image.")

            logger.warning("There are no available blends linked w/ pngs for importing!")
            return {'CANCELLED'}

        path = os.path.join(addon_prefs.tiles_path, mg.tiles + ".blend")

        if os.access(path, os.R_OK):
            utils.append_objs(path)
            bpy.ops.object.select_all(action='DESELECT')
            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "The selected tile set could not be imported! \nPlease send a bug report; this should never happen.")
            return {'CANCELLED'}


class EnableLayerMG(Operator):
    bl_label = "Enable First Layer"
    bl_idname = "maze_gen.enable_layer"
    bl_description = "Enables first layer so UltiMaze can work :)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        logger.warning("Enabling the first layer...this shouldn't be a problem, but also not spectacularly awesome either!")
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


class MazeGenPropertyGroup(PropertyGroup):
    """These are all of the properties for the maze generator."""

    # ---------------------- General Settings -------------------------

    mg_width = IntProperty(
        name="Width", default=25, min=3, max=999)

    mg_height = IntProperty(
        name="Height", default=25, min=3, max=999)

    gen_3d_maze = BoolProperty(
        name="gen_3d_maze",
        default=True)

    # --------------------------- Tiles -------------------------------

    wall_4_sided = StringProperty(
        name="wall_4_sided",
        default="wall_4_sided",
        description="Wall piece with 4 sides")

    wall_3_sided = StringProperty(
        name="wall_3_sided",
        default="wall_3_sided",
        description="Wall piece with 3 sides")

    wall_2_sided = StringProperty(
        name="wall_2_sided",
        default="wall_2_sided",
        description="Wall piece with 2 opposite sides")

    wall_1_sided = StringProperty(
        name="wall_1_sided",
        default="wall_1_sided",
        description="Wall piece with 1 side")

    wall_0_sided = StringProperty(
        name="wall_0_sided",
        default="wall_0_sided",
        description="Wall piece with 0 sides")

    wall_corner = StringProperty(
        name="wall_corner",
        default="wall_corner",
        description="Wall piece with 2 adjacent sides")

    floor_4_sided = StringProperty(
        name="floor_4_sided",
        default="floor_4_sided",
        description="Floor piece with 4 sides")

    floor_3_sided = StringProperty(
        name="floor_3_sided",
        default="floor_3_sided",
        description="Floor piece with 3 sides")

    floor_2_sided = StringProperty(
        name="floor_2_sided",
        default="floor_2_sided",
        description="Floor piece with 2 opposite sides")

    floor_1_sided = StringProperty(
        name="floor_1_sided",
        default="floor_1_sided",
        description="Floor piece with 1 side")

    floor_0_sided = StringProperty(
        name="floor_0_sided",
        default="floor_0_sided",
        description="Floor piece with 0 sides")

    floor_corner = StringProperty(
        name="floor_corner",
        default="floor_corner",
        description="Floor piece with 2 adjacent sides")

    four_way = StringProperty(
        name="four_way",
        default="four_way",
        description="4-way (+) intersection")

    t_int = StringProperty(
        name="t_int",
        default="t_int",
        description="3-way (T) intersection")

    turn = StringProperty(
        name="turn",
        default="turn",
        description="2-way (L) intersection")

    dead_end = StringProperty(
        name="dead_end",
        default="dead_end",
        description="Dead-end (]) tile")

    straight = StringProperty(
        name="straight",
        default="straight",
        description="Straight (|) tile")

    no_path = StringProperty(
        name="no_path",
        default="no_path",
        description="Wall-only (0) tile")

    # ----------------------- Tile Settings ---------------------------

    tile_based = BoolProperty(
        name="tile_based", default=False)

    tile_mode = EnumProperty(
        items=[('TWELVE_TILES', "12-Piece Mode", "Use 12 tile pieces."),
               ('SIX_TILES', "6-Piece Mode", "Use 6 tile pieces.")],
        name="Tile Mode",
        description="Number of tiles to use.",
        default="TWELVE_TILES")

    import_mat = BoolProperty(
        name="import_mat",
        default=True)

    merge_objects = BoolProperty(
        name="merge_objects",
        default=True)

    remove_doubles_merge = BoolProperty(
        name="remove_doubles_merge",
        default=True)

    apply_modifiers = BoolProperty(
        name="apply_modifiers",
        default=True)

    tiles = EnumProperty(name="Tile", items=enum_previews_from_directory)

    tile_importer = BoolProperty(name="Tile Importer", default=False)

    # ----------------------- List Settings ---------------------------

    list_maze = StringProperty(
        name="list_maze",
        default="")

    use_list_maze = BoolProperty(
        name="use_list_maze",
        default=False,
        description="Generate maze from 1s and 0s from text data block")

    write_list_maze = BoolProperty(
        name="write_list_maze",
        default=False)

    # ------------------------ Loop Adding ----------------------------

    allow_loops = BoolProperty(
        name="allow_loops",
        default=False)

    loops_chance = IntProperty(
        name="loops_chance",
        default=3,
        min=1,
        max=1000000,
        description="1/x chance of creating each possible loop")

    # -------------------- Algorithm Settings -------------------------

    algorithm = EnumProperty(
        items=[('DEPTH_FIRST', "Depth-First", ""),
               ('BREADTH_FIRST', "Breadth-First", ""),
               ('PRIMS', "Prim's", ""),
               ('BINARY_TREE', "Binary Tree", ""),
               ('KRUSKALS', "Kruskal's", ""),
               ('ELLERS', "Eller's", "")],
        name="Algorithm",
        description="Algorithm to use when generating maze paths internally",
        default="DEPTH_FIRST")

    binary_dir = EnumProperty(
        items=[('RANDOM', "Random", ""),
               ('NE', "North-East", ""),
               ('NW', "North-West", ""),
               ('SE', "South-East", ""),
               ('SW', "South-West", "")],
        name="Binary Tree Direction",
        description="Bias diagonal for binary tree maze algorithm",
        default="RANDOM")

    tileable = BoolProperty(
        name="Tileable",
        description="Makes resulting maze tileable",
        default=True)

    bias_direction = EnumProperty(
        items=[('RANDOM', "Random", ""),
               ('X', "X-Axis", ""),
               ('Y', "Y-Axis", "")],
        name="Bias Direction",
        description="Bias direction for graph theory based algorithms",
        default="RANDOM")

    bias = FloatProperty(
        name="Bias",
        description="Amount of bias for graph theory based algorithms:\n    0 = no bias\n    1 = high bias",
        default=0,
        min=0,
        max=1)

    # ----------------------- Batch Tools -----------------------------

    num_batch_mazes = IntProperty(
        name="num_batch_mazes",
        default=0,
        min=0,
        max=1000000,
        description="Number of mazes to batch generate")

    batch_index = IntProperty(
        name="batch_index",
        default=1,
        min=1,
        max=1000000,
        description="Batch index to load stored setting")

    # -------------------- Text Find/Replace --------------------------

    text1_mg = StringProperty(
        name="text1_mg",
        default="")

    text2_mg = StringProperty(
        name="text2_mg",
        default="")

    # ------------------------ Image Maze -----------------------------

    maze_image = StringProperty(
        name="maze_image",
        default="")

    # ------------------------ Help Enums -----------------------------

    generation_desire = EnumProperty(
        items=[('SIMP_3D', "Simple 3D Maze", ""),
               ('TILE_MAZE', "Tile Maze", ""),
               ('TEXT_MAZE', "Text Maze", ""),
               ('IMAGE_MAZE', "Image Maze", "")],
        name="Desired",
        description="What would you like to have?",
        default="SIMP_3D")

    user_provision = EnumProperty(
        items=[('SETTINGS', "Layout Settings", ""),
               ('IMAGE_MAZE', "Image Maze", ""),
               ('TEXT_MAZE', "Text Maze", "")],
        name="You Have",
        description="What do you have?",
        default="SETTINGS")


# classes to register
classes = [MazeAddonPrefsMg,
           # Main
           GenerateMazeMG,
           DemoTilesImportMG,
           ShowHelpDiagramMG,
           ShowReadmeMG,
           MazeGenPropertyGroup,
           render_kit.RenderTileSet,
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
           RescanTilesPath,
           LoadOriginalTilesPath,
           bug_reporter.ReportABug,
           # Menus
           menus.TileRenderMenu,
           menus.EnableLayerMenu]

preview_collections = {}


def register():
    # third-party add-on updater
    addon_updater_ops.register(bl_info)

    save_addon_name(basename(dirname(__file__)))

    ascii_logo.display_ascii_logo()

    for i in classes:
        register_class(i)

    Scene.mg = PointerProperty(type=MazeGenPropertyGroup)

    set_main_pcoll(preview_collections)


def unregister():
    for i in classes:
        unregister_class(i)

    del Scene.mg

    clear_preview_collections(preview_collections)


if __name__ == "__main__":
    register()
