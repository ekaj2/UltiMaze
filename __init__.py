# TODO - LEGAL

"""
===== MAZE GENERATOR [PRO] V.1.0 =====
This __init__ module handles some UI and also registers all
classes and properties.

Available Functions:
    import_mat - Imports material if not in .blend
"""

bl_info = {
    "name": "UltiMaze [PRO]",
    "author": "Jake Dube",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "3D View > Tools > Maze Gen",
    "description": "Generates 3-dimensional mazes.",
    "warning": "May take a long time to generate maze: "
               "see quick help below.",
    "wiki_url": "",
    "category": "3D View",
}

import os
import time

import bpy
from maze_gen import auto_layout_gen
from maze_gen import batch_gen
from maze_gen import prep_manager
from maze_gen import simple_maze_gen
from maze_gen import text_tools
from maze_gen import tile_maze_gen
from maze_gen import time_log
from maze_gen import txt_img_converter


def import_mat(material_type, my_tiles_dir):
    """Imports material if not in .blend.

    Args:
        material_type - type of material to change logic (not used much now)
        my_tiles_dir - directory where material_lib.blend is located

    Returns:
        actual name of imported material
    """
    my_blend_filepath = os.path.join(my_tiles_dir, "material_lib.blend")
    my_blend_directory = os.path.join(my_blend_filepath, "Material")

    if material_type == 'DEFAULT':

        if bpy.context.scene.render.engine == 'CYCLES':
            mat_in_blend = True
            try:
                bpy.data.materials['maze_default_cycles']
            except KeyError:
                mat_in_blend = False
            if not mat_in_blend:
                bpy.ops.wm.append(
                    filepath=("//material_lib.blend/Material/" +
                              "maze_default_cycles"),
                    filename="maze_default_cycles",
                    directory=my_blend_directory,
                    autoselect=False)

            return "maze_default_cycles"

        else:
            mat_in_blend = True
            try:
                bpy.data.materials['maze_default_bi']
            except KeyError:
                print("\nBI mat not in .blend.\n")
                mat_in_blend = False
            if not mat_in_blend:
                bpy.ops.wm.append(
                    filepath="//material_lib.blend/Material/maze_default_bi",
                    filename="maze_default_bi",
                    directory=my_blend_directory,
                    autoselect=False)

            return "maze_default_bi"

    return ""


# UI Classes
# 3D View
class MazeGeneratorPanelMG(bpy.types.Panel):
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
        row.operator("object.generate_maze", icon="MOD_BUILD")

        # layout settings box
        box = layout.box()
        box.label("Layout Settings", icon='SETTINGS')
        box.prop(scene, 'mg_width', slider=False, text="Width")
        box.prop(scene, 'mg_height', slider=False, text="Height")
        box.prop(scene, 'gen_3d_maze', text="Generate 3D Maze")
        row = box.row()
        row.prop(scene, 'allow_loops', text="Allow Loops")
        row.prop(scene, 'loops_chance', text="Chance")

        row = box.row()
        row.prop(scene, 'allow_islands', text="Allow 'Islands'")

        if scene.use_list_maze:
            row.enabled = False
        else:
            row.enabled = True

        box.prop(scene, 'use_list_maze', text="Generate Maze From List")
        if scene.use_list_maze:
            box.prop_search(scene, 'list_maze', bpy.data, 'texts', text="List Maze")

        # write list maze box
        box = layout.box()
        box.prop(scene, 'write_list_maze', text="Write Maze List")


class ImageConverterPanelMG(bpy.types.Panel):
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
        row.label("(X: " + str(scene.mg_width) + ", Y: " + str(scene.mg_height) + ")")  # TODO - New string.format
        box.operator("scene.convert_maze_image", icon="TEXT")
        box.prop_search(scene, 'maze_image', bpy.data, "images", "Image Maze")

        box.operator("scene.create_image_from_list", icon="IMAGE_COL")
        box.prop_search(scene, 'list_maze', bpy.data, "texts", "List Maze")


class MazeTilesPanelMG(bpy.types.Panel):
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
            row = sub_box.row(align=True)
            row.operator("object.generate_demo_tiles", icon="MOD_SOLIDIFY")
            row.prop(scene, 'tile_set_type', text="")
            sub_box.prop(context.scene, 'import_mat', text="Import Material")

            sub_box = box.box()
            sub_box.prop(context.scene, 'merge_objects', text="Merge Objects")
            if scene.merge_objects:
                sub_box.prop(context.scene, 'apply_modifiers', text="Apply Modifiers")
                sub_box.prop(context.scene, 'remove_doubles_merge', text="Remove Doubles")

            row = layout.row()
            row.separator()

            box = layout.box()
            box.label("Tiles", icon='MESH_GRID')
            # list of tiles types needed
            col = box.column()
            if scene.tile_mode == "TWELVE_TILES":
                col.label("Wall Pieces:")
                col.prop_search(context.scene, 'wall_4_sided', bpy.data, "objects", "4 Sided Wall")
                col.prop_search(context.scene, 'wall_3_sided', bpy.data, "objects", "3 Sided Wall")
                col.prop_search(context.scene, 'wall_2_sided', bpy.data, "objects", "2 Sided Wall")
                col.prop_search(context.scene, 'wall_1_sided', bpy.data, "objects", "1 Sided Wall")
                col.prop_search(context.scene, 'wall_0_sided', bpy.data, "objects", "0 Sided Wall")
                col.prop_search(context.scene, 'wall_corner', bpy.data, "objects", "Wall Corner")

                col = box.column()
                col.label("Floor Pieces:")
                col.prop_search(context.scene, 'floor_4_sided', bpy.data, "objects", "4 Sided Floor")
                col.prop_search(context.scene, 'floor_3_sided', bpy.data, "objects", "3 Sided Floor")
                col.prop_search(context.scene, 'floor_2_sided', bpy.data, "objects", "2 Sided Floor")
                col.prop_search(context.scene, 'floor_1_sided', bpy.data, "objects", "1 Sided Floor")
                col.prop_search(context.scene, 'floor_0_sided', bpy.data, "objects", "0 Sided Floor")
                col.prop_search(context.scene, 'floor_corner', bpy.data, "objects", "Floor Corner")
            elif scene.tile_mode == "SIX_TILES":
                col.label("Pieces:")
                col.prop_search(context.scene, 'four_way', bpy.data, "objects", "4-Way")
                col.prop_search(context.scene, 't_int', bpy.data, "objects", "3-Way")
                col.prop_search(context.scene, 'turn', bpy.data, "objects", "Turn")
                col.prop_search(context.scene, 'dead_end', bpy.data, "objects", "Dead End")
                col.prop_search(context.scene, 'straight', bpy.data, "objects", "Straight Path")
                col.prop_search(context.scene, 'no_path', bpy.data, "objects", "Wall Only")


class BatchGeneratorPanelMG(bpy.types.Panel):
    bl_label = "Batch Gen [PRO]"
    bl_idname = "3D_VIEW_PT_layout_BatchGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Maze Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("scene.batch_generate_maze", icon="PACKAGE")
        box.operator("scene.store_batch_maze", icon="FILE")

        row = box.row(align=True)
        row.operator("scene.refresh_batch_num", icon="LOAD_FACTORY")
        sub_col = row.column()
        sub_col.enabled = False
        sub_col.prop(context.scene, 'num_batch_mazes', text="Batches")

        box.operator("scene.clear_batch_maze", icon="CANCEL")

        row = layout.row()
        row.separator()

        box = layout.box()
        box.prop(context.scene, 'batch_index', text="Batch Index")
        box.operator("scene.load_batch_maze", icon="OOPS")
        box.operator("scene.delete_batch_maze", icon="X")


class InfoPanelMG(bpy.types.Panel):
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
        box.operator("scene.show_workflows_image", icon="OOPS")
        box.operator("scene.show_readme_text", icon="FILE_TEXT")

        row = layout.row()
        row.separator()

        # time settings box
        box = layout.box()
        box.label("Time Estimate", icon="TIME")
        col = box.column()
        col.operator("object.estimate_time_mg", icon="QUESTION")


class HelpPanelMG(bpy.types.Panel):
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


class MazeAddonPrefsMg(bpy.types.AddonPreferences):
    bl_idname = __name__

    always_save_prior = bpy.props.BoolProperty(
        name="always_save_prior",
        default=True,
        description="Always save .blend file before executing" +
                    "time-consuming operations")

    save_all_images = bpy.props.BoolProperty(
        name="save_all_images",
        default=True,
        description="Always save images before executing" +
                    "time-consuming operations")

    save_all_texts = bpy.props.BoolProperty(
        name="save_all_texts",
        default=True,
        description="Always save texts before executing" +
                    "time-consuming operations")

    show_quickhelp = bpy.props.BoolProperty(
        name="show_quickhelp",
        default=False,
        description="Show quick help")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, 'always_save_prior', text="Save .blend File")
        row = layout.row()
        row.prop(self, 'save_all_images', text="Save Images")
        row = layout.row()
        row.prop(self, 'save_all_texts', text="Save Texts")

        layout.row()

        # quick help box
        box = layout.box()

        show_help_text = "Show Quick Help"
        if self.show_quickhelp:
            show_help_text = "Hide Quick Help"
        row = box.row()
        row.prop(self, "show_quickhelp", text=show_help_text, toggle=True)
        if self.show_quickhelp:
            box.row()

            row = box.row()
            row.scale_y = 0.5
            row.label(text="If Blender locks up where you have unsaved work " +
                           "and you are fortunate enough to have found this do not")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="close Blender . . . yet. Read this first and/or " +
                           "contact support, if needed, to try to salvage your progress.")

            box.row()

            row = box.row()
            row.scale_y = 0.5
            row.label(text="The amount of time for most maze operations to " +
                           "complete will increase exponentially with the size " +
                           "of the maze.")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="Blender freezes its UI when scripts are " +
                           "executing, however, this can be combated with a few " +
                           "tricks as follows")

            # blank row for paragraph
            box.row()

            row = box.row()
            row.scale_y = 0.5
            row.label(text="First, open a system console window (for " +
                           "Windows available from Info Header > Window > Toggle " +
                           "System Console)")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="to see progress as a percent or to stop the " +
                           "operation (with Ctrl-C). It is important to have this open " +
                           "before")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="starting an operation, because it can't easily " +
                           "be opened after you start an operator " +
                           "(by pressing any UI button).")

            box.row()

            row = box.row()
            row.scale_y = 0.5
            row.label(text="Another useful tip is to always save your work " +
                           "before generating anything or use a blank " +
                           ".blend file for generation.")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="This will allow you to force Blender to close " +
                           "without losing your work. This can be done automatically " +
                           "by leaving the")
            row = box.row()
            row.scale_y = 0.5
            row.label(text="3 checkboxes above (Save .blend File, " +
                           "Save Images . . . ) enabled.")

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
        row.operator("wm.url_open", text="Support E-Mail",
                     icon='LINENUMBERS_ON').url = "mailto: assetsupport@integrity-sg.com"


# Text Editor
class MazeGeneratorTextToolsPanelMG(bpy.types.Panel):
    bl_label = "Maze Generator Tools"
    bl_idname = "TEXT_EDITOR_PT_layout_MazeGenerator"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop_search(
            context.scene, 'list_maze', bpy.data, 'texts', text="List Maze")

        box = layout.box()
        box.operator("scene.invert_text_mg", icon="ARROW_LEFTRIGHT")

        box = layout.box()
        box.operator("scene.replace_text_mg", icon="FONT_DATA")
        box.prop(context.scene, 'text1_mg', text="Find")
        box.prop(context.scene, 'text2_mg', text="Replace")


class ShowHelpDiagramMG(bpy.types.Operator):
    bl_label = "Workflows Diagram"
    bl_idname = "scene.show_workflows_image"
    bl_description = "Shows a workflow diagram in the image editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        my_directory = os.path.join(os.path.dirname(__file__), "help")
        image_filepath = os.path.join(my_directory, "Workflow Diagram.png")

        bpy.ops.image.open(filepath=image_filepath,
                           directory=my_directory,
                           files=[{"name": "Workflow Diagram.png"}],
                           relative_path=True,
                           show_multiview=False)

        self.report({'INFO'}, "See workflow diagram in the image editor")

        return {'FINISHED'}


class ShowReadmeMG(bpy.types.Operator):
    bl_label = "Readme"
    bl_idname = "scene.show_readme_text"
    bl_description = "Shows readme in the text editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        my_directory = os.path.join(os.path.dirname(__file__), "help")
        my_filepath = os.path.join(my_directory, "Readme.txt")

        bpy.ops.text.open(filepath=my_filepath)

        self.report({'INFO'}, "See readme in the text editor")

        return {'FINISHED'}


# demo tile objects generation
class DemoTilesMG(bpy.types.Operator):
    bl_label = "Generate Tiles"
    bl_idname = "object.generate_demo_tiles"
    bl_description = "Generates basic tiles."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        my_tiles_dir = os.path.join(os.path.dirname(__file__), "tiles")

        if scene.tile_set_type == 'DEMO':
            my_filepath = os.path.join(my_tiles_dir, "tile_demo.fbx")

        elif scene.tile_set_type == 'BLANK':
            my_filepath = os.path.join(my_tiles_dir, "tile_blanks.fbx")

        elif scene.tile_set_type == 'ROUNDED':
            my_filepath = os.path.join(my_tiles_dir, "tile_rounded.fbx")

        elif scene.tile_set_type == 'PIPING':
            my_filepath = os.path.join(my_tiles_dir, "tile_piping.fbx")

        # import .fbx
        bpy.ops.wm.addon_enable(module="io_scene_fbx")
        bpy.ops.import_scene.fbx(filepath=my_filepath)

        # setup a material importer ! ! !
        if scene.import_mat:
            material = import_mat("DEFAULT", my_tiles_dir)

            # link materials to models
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
            bpy.ops.object.material_slot_add()

            # try this ...
            bpy.context.scene.objects.active.id_data.material_slots[0].material = bpy.data.materials[material]
            # (bpy.data.objects[bpy.context.scene.objects.active.name].
            #    material_slots[0].material) = bpy.data.materials[material]
            bpy.ops.object.make_links_data(type='MATERIAL')

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


# main maze gen controller
class GenerateMazeMG(bpy.types.Operator):
    bl_label = "Generate Maze"
    bl_idname = "object.generate_maze"
    bl_description = "Generates a 3D maze"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        time_start = time.time()

        if scene.tile_based and scene.gen_3d_maze:
            tiles_exist = prep_manager.check_tiles_exist()

            # if missing tiles: terminate operator
            if not tiles_exist:
                self.report({'ERROR'}, "One or more tile objects is missing " +
                            "or is not a mesh! Please assign a valid object or " +
                            "disable 'Use Modeled Tiles'.")
                return {'CANCELLED'}

        if scene.use_list_maze:
            list_exist = prep_manager.check_list_exist()

            # if missing list: terminate operator
            if not list_exist:
                self.report({'ERROR'}, "List missing! Please assign a valid " +
                            "text data block or disable 'Generate Maze From List'.")
                return {'CANCELLED'}

        # save files
        save_return, bad_file = prep_manager.always_save()
        if save_return == "BLEND_ERROR":
            self.report({'ERROR'}, "Save file or disable always save " +
                        "in user prefs.")
            return {'CANCELLED'}

        elif save_return == "IMAGE_ERROR":
            self.report({'ERROR'}, "Image '" + bad_file.name +
                        "' does not have a valid file path (for saving). Assign " +
                        "a valid path, pack image, or disable save images in " +
                        "user prefs")
            return {'CANCELLED'}

        elif save_return == "TEXT_ERROR":
            self.report({'ERROR'}, "Text '" + bad_file.name +
                        "' does not have a valid file path (for saving). " +
                        "Assign a valid path or disable save texts in user prefs")
            return {'CANCELLED'}

        apply_mods = scene.apply_modifiers
        if not scene.merge_objects:
            # fix to make sure not applying modifiers
            # if merging is disabled (because group is not made)
            scene.apply_modifiers = False

        if scene.use_list_maze:
            maze = txt_img_converter.convert_list_maze()
        elif scene.gen_3d_maze or scene.use_list_maze or scene.write_list_maze:
            maze = auto_layout_gen.make_list_maze()

        if scene.allow_loops:
            maze = auto_layout_gen.add_loops(maze)

        # 3D generation
        if bpy.context.scene.gen_3d_maze:
            if scene.tile_based:
                tile_maze_gen.make_tile_maze(maze)
            else:
                simple_maze_gen.make_3dmaze(maze)

        scene.apply_modifiers = apply_mods

        # log time
        if scene.gen_3d_maze:
            time_log.log_time(time.time() - time_start)

        if scene.gen_3d_maze or scene.write_list_maze:
            self.report({'INFO'}, "Finished generating maze in " +
                        str(time.time() - time_start) + " seconds")

        # write list maze if enabled
        if scene.write_list_maze:
            text_block_name = txt_img_converter.str_list_maze(maze)
            self.report({'INFO'}, "See '" + str(text_block_name) +
                        "' in the text editor")

        return {'FINISHED'}


# classes to register
classes = [GenerateMazeMG, batch_gen.BatchGenerateMazeMG,
           batch_gen.StoreBatchMazeMG, batch_gen.ClearBatchMazesMG,
           batch_gen.RefreshBatchMazesMG, batch_gen.LoadBatchMazeMG,
           batch_gen.DeleteBatchMazeMG, time_log.EstimateTimeMG,
           MazeGeneratorPanelMG, ImageConverterPanelMG, MazeTilesPanelMG,
           BatchGeneratorPanelMG, InfoPanelMG, HelpPanelMG, DemoTilesMG,
           MazeGeneratorTextToolsPanelMG, text_tools.ReplaceTextMG,
           text_tools.InvertTextMG, txt_img_converter.ConvertMazeImageMG,
           txt_img_converter.CreateImageFromListMG, ShowHelpDiagramMG,
           ShowReadmeMG, MazeAddonPrefsMg]


def register():
    for i in classes:
        bpy.utils.register_class(i)

    bpy.types.Scene.mg_width = bpy.props.IntProperty(
        name="Width", default=25, min=3, max=1000)
    bpy.types.Scene.mg_height = bpy.props.IntProperty(
        name="Height", default=25, min=3, max=1000)
    bpy.types.Scene.tile_based = bpy.props.BoolProperty(
        name="tile_based", default=False)

    # type of pieces to add
    bpy.types.Scene.tile_set_type = bpy.props.EnumProperty(
        items=[('BLANK', "Blank", "Completely blank tiles"),
               ('DEMO', "Demo", "Simple design on tiles"),
               ('PIPING', "Piping", "A piping tileset also demonstrates ability to " +
                "use parenting to have different modifiers for parts of a tile"),
               ('ROUNDED', "Rounded", "Demonstrates how to model rounding " +
                "at top of tiles")],
        name="Tile Set",
        description="Tile set to add",
        default="BLANK")

    bpy.types.Scene.tile_mode = bpy.props.EnumProperty(
        items=[('TWELVE_TILES', "12-Piece Mode", "Use 12 tile pieces."),
               ('SIX_TILES', "6-Piece Mode", "Use 6 tile pieces.")],
        name="Tile Mode",
        description="Number of tiles to use.",
        default="TWELVE_TILES")

    # wall pieces
    bpy.types.Scene.wall_4_sided = bpy.props.StringProperty(
        name="wall_4_sided",
        default="wall_4_sided",
        description="Wall piece with 4 sides")

    bpy.types.Scene.wall_3_sided = bpy.props.StringProperty(
        name="wall_3_sided",
        default="wall_3_sided",
        description="Wall piece with 3 sides")

    bpy.types.Scene.wall_2_sided = bpy.props.StringProperty(
        name="wall_2_sided",
        default="wall_2_sided",
        description="Wall piece with 2 opposite sides")

    bpy.types.Scene.wall_1_sided = bpy.props.StringProperty(
        name="wall_1_sided",
        default="wall_1_sided",
        description="Wall piece with 1 side")

    bpy.types.Scene.wall_0_sided = bpy.props.StringProperty(
        name="wall_0_sided",
        default="wall_0_sided",
        description="Wall piece with 0 sides")

    bpy.types.Scene.wall_corner = bpy.props.StringProperty(
        name="wall_corner",
        default="wall_corner",
        description="Wall piece with 2 adjacent sides")

    # floor pieces
    bpy.types.Scene.floor_4_sided = bpy.props.StringProperty(
        name="floor_4_sided",
        default="floor_4_sided",
        description="Floor piece with 4 sides")

    bpy.types.Scene.floor_3_sided = bpy.props.StringProperty(
        name="floor_3_sided",
        default="floor_3_sided",
        description="Floor piece with 3 sides")

    bpy.types.Scene.floor_2_sided = bpy.props.StringProperty(
        name="floor_2_sided",
        default="floor_2_sided",
        description="Floor piece with 2 opposite sides")

    bpy.types.Scene.floor_1_sided = bpy.props.StringProperty(
        name="floor_1_sided",
        default="floor_1_sided",
        description="Floor piece with 1 side")

    bpy.types.Scene.floor_0_sided = bpy.props.StringProperty(
        name="floor_0_sided",
        default="floor_0_sided",
        description="Floor piece with 0 sides")

    bpy.types.Scene.floor_corner = bpy.props.StringProperty(
        name="floor_corner",
        default="floor_corner",
        description="Floor piece with 2 adjacent sides")

    bpy.types.Scene.four_way = bpy.props.StringProperty(
        name="four_way",
        default="four_way",
        description="4-way (+) intersection")

    bpy.types.Scene.t_int = bpy.props.StringProperty(
        name="t_int",
        default="t_int",
        description="3-way (T) intersection")

    bpy.types.Scene.turn = bpy.props.StringProperty(
        name="turn",
        default="turn",
        description="2-way (L) intersection")

    bpy.types.Scene.dead_end = bpy.props.StringProperty(
        name="dead_end",
        default="dead_end",
        description="Dead-end (]) tile")

    bpy.types.Scene.straight = bpy.props.StringProperty(
        name="straight",
        default="straight",
        description="Straight (|) tile")

    bpy.types.Scene.no_path = bpy.props.StringProperty(
        name="no_path",
        default="no_path",
        description="Wall-only (0) tile")

    bpy.types.Scene.import_mat = bpy.props.BoolProperty(
        name="import_mat",
        default=True)

    bpy.types.Scene.merge_objects = bpy.props.BoolProperty(
        name="merge_objects",
        default=True)

    bpy.types.Scene.remove_doubles_merge = bpy.props.BoolProperty(
        name="remove_doubles_merge",
        default=True)

    bpy.types.Scene.apply_modifiers = bpy.props.BoolProperty(
        name="apply_modifiers",
        default=True)

    bpy.types.Scene.list_maze = bpy.props.StringProperty(
        name="list_maze",
        default="")

    bpy.types.Scene.use_list_maze = bpy.props.BoolProperty(
        name="use_list_maze",
        default=False,
        description="Generate maze from 1s and 0s from text data block")

    bpy.types.Scene.write_list_maze = bpy.props.BoolProperty(
        name="write_list_maze",
        default=False)

    bpy.types.Scene.allow_loops = bpy.props.BoolProperty(
        name="allow_loops",
        default=False)

    bpy.types.Scene.allow_islands = bpy.props.BoolProperty(
        name="allow_islands",
        default=False,
        description="Allow pieces connected only by a corner")

    bpy.types.Scene.loops_chance = bpy.props.IntProperty(
        name="loops_chance",
        default=3,
        min=1,
        max=1000000,
        description="1/x chance of creating each possible loop")

    bpy.types.Scene.num_batch_mazes = bpy.props.IntProperty(
        name="num_batch_mazes",
        default=0,
        min=0,
        max=1000000,
        description="Number of mazes to batch generate")

    bpy.types.Scene.batch_index = bpy.props.IntProperty(
        name="batch_index",
        default=1,
        min=1,
        max=1000000,
        description="Batch index to load stored setting")

    bpy.types.Scene.gen_3d_maze = bpy.props.BoolProperty(
        name="gen_3d_maze",
        default=True)

    bpy.types.Scene.text1_mg = bpy.props.StringProperty(
        name="text1_mg",
        default="")

    bpy.types.Scene.text2_mg = bpy.props.StringProperty(
        name="text2_mg",
        default="")

    bpy.types.Scene.maze_image = bpy.props.StringProperty(
        name="maze_image",
        default="")

    # help enums
    bpy.types.Scene.generation_desire = bpy.props.EnumProperty(
        items=[('SIMP_3D', "Simple 3D Maze", ""),
               ('TILE_MAZE', "Tile Maze", ""),
               ('TEXT_MAZE', "Text Maze", ""),
               ('IMAGE_MAZE', "Image Maze", "")],
        name="Desired",
        description="What would you like to have?",
        default="SIMP_3D")

    bpy.types.Scene.user_provision = bpy.props.EnumProperty(
        items=[('SETTINGS', "Layout Settings", ""),
               ('IMAGE_MAZE', "Image Maze", ""),
               ('TEXT_MAZE', "Text Maze", "")],
        name="You Have",
        description="What do you have?",
        default="SETTINGS")


def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)

    del bpy.types.Scene.mg_width
    del bpy.types.Scene.mg_height
    del bpy.types.Scene.tile_based

    del bpy.types.Scene.tile_set_type
    del bpy.types.Scene.tile_mode

    del bpy.types.Scene.wall_4_sided
    del bpy.types.Scene.wall_3_sided
    del bpy.types.Scene.wall_2_sided
    del bpy.types.Scene.wall_1_sided
    del bpy.types.Scene.wall_0_sided
    del bpy.types.Scene.wall_corner

    del bpy.types.Scene.floor_4_sided
    del bpy.types.Scene.floor_3_sided
    del bpy.types.Scene.floor_2_sided
    del bpy.types.Scene.floor_1_sided
    del bpy.types.Scene.floor_0_sided
    del bpy.types.Scene.floor_corner

    del bpy.types.Scene.four_way
    del bpy.types.Scene.t_int
    del bpy.types.Scene.turn
    del bpy.types.Scene.straight
    del bpy.types.Scene.dead_end
    del bpy.types.Scene.no_path

    del bpy.types.Scene.import_mat

    del bpy.types.Scene.merge_objects
    del bpy.types.Scene.apply_modifiers
    del bpy.types.Scene.remove_doubles_merge

    del bpy.types.Scene.list_maze
    del bpy.types.Scene.use_list_maze
    del bpy.types.Scene.write_list_maze

    del bpy.types.Scene.allow_loops
    del bpy.types.Scene.allow_islands
    del bpy.types.Scene.loops_chance

    del bpy.types.Scene.num_batch_mazes
    del bpy.types.Scene.batch_index

    del bpy.types.Scene.gen_3d_maze

    del bpy.types.Scene.text1_mg
    del bpy.types.Scene.text2_mg

    del bpy.types.Scene.maze_image

    del bpy.types.Scene.generation_desire
    del bpy.types.Scene.user_provision


if __name__ == "__main__":
    register()
