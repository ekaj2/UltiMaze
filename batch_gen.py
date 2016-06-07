"""
Batch tools for mazes

Available Functions:
    refresh_batch_max - Refreshes number of batch mazes by checking txt file
"""

import os
import time

import bpy
from maze_gen import auto_layout_gen
from maze_gen import prep_manager
from maze_gen import simple_maze_gen
from maze_gen import tile_maze_gen
from maze_gen import time_log
from maze_gen import txt_img_converter


def refresh_batch_max():
    """Refreshes number of batch mazes by checking txt file."""
    my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
    maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

    with open(maze_setups_file, "r") as s:
        settings_text = s.read()

    settings_text = settings_text.replace(" && ", "", 1)

    split_settings = settings_text.split(" && ")

    if settings_text == "":
        bpy.context.scene.num_batch_mazes = 0
    else:
        bpy.context.scene.num_batch_mazes = len(split_settings)


class StoreBatchMazeMG(bpy.types.Operator):
    bl_label = "Store Settings"
    bl_idname = "scene.store_batch_maze"
    bl_description = "Stores a maze to batch generate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        settings_text = (" && wd,{};ht,{};3d,{};al,{};lc,{};ai,{}"
                         ";fl,{};lm,{};wl,{};tb,{};im,{};mo,{};am,{};rd,{}"
                         ";w0,{};w1,{};w2,{};w3,{};w4,{};wc,{}"
                         ";f0,{};f1,{};f2,{};f3,{};f4,{};fc,{}".format(
                            scene.mg_width,
                            scene.mg_height,
                            int(scene.gen_3d_maze),
                            int(scene.allow_loops),
                            scene.loops_chance,
                            int(scene.allow_islands),
                            int(scene.use_list_maze),
                            scene.list_maze,
                            int(scene.write_list_maze),
                            int(scene.tile_based),
                            int(scene.import_mat),
                            int(scene.merge_objects),
                            int(scene.apply_modifiers),
                            int(scene.remove_doubles_merge),
                            scene.wall_0_sided,
                            scene.wall_1_sided,
                            scene.wall_2_sided,
                            scene.wall_3_sided,
                            scene.wall_4_sided,
                            scene.wall_corner,
                            scene.floor_0_sided,
                            scene.floor_1_sided,
                            scene.floor_2_sided,
                            scene.floor_3_sided,
                            scene.floor_4_sided,
                            scene.floor_corner))

        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "a") as s:
            print(settings_text, end="", file=s, flush=True)

        scene.num_batch_mazes += 1

        return {'FINISHED'}


class ClearBatchMazesMG(bpy.types.Operator):
    bl_label = "Clear Mazes"
    bl_idname = "scene.clear_batch_maze"
    bl_description = "Clears all mazes from batch cache."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "w") as s:
            s.write("")

        scene.num_batch_mazes = 0

        return {'FINISHED'}


class RefreshBatchMazesMG(bpy.types.Operator):
    bl_label = "Refresh"
    bl_idname = "scene.refresh_batch_num"
    bl_description = "Refreshes number of batches."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_batch_max()
        return {'FINISHED'}


class LoadBatchMazeMG(bpy.types.Operator):
    bl_label = "Load Settings"
    bl_idname = "scene.load_batch_maze"
    bl_description = "Loads the maze settings for batch number."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        refresh_batch_max()

        if scene.num_batch_mazes == 0:
            self.report({'ERROR'}, "No mazes stored!")
            return {'CANCELLED'}

        if scene.batch_index > scene.num_batch_mazes:
            scene.batch_index = scene.num_batch_mazes
            self.report({'ERROR'}, "Not a maze index! Setting to highest " +
                        "batched maze number...")
            return {'CANCELLED'}

        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)

        split_settings = settings_text.split(" && ")

        maze_setup = split_settings[scene.batch_index - 1]

        maze_setup = maze_setup.split(";")

        for slot in maze_setup:
            parts = slot.split(",")

            # main settings
            if parts[0] == "wd":
                scene.mg_width = int(parts[1])
            elif parts[0] == "ht":
                scene.mg_height = int(parts[1])
            elif parts[0] == "3d":
                scene.gen_3d_maze = bool(int(parts[1]))
            elif parts[0] == "al":
                scene.allow_loops = bool(int(parts[1]))
            elif parts[0] == "lc":
                scene.loops_chance = int(parts[1])
            elif parts[0] == "ai":
                scene.allow_islands = bool(int(parts[1]))
            elif parts[0] == "fl":
                scene.use_list_maze = bool(int(parts[1]))
            elif parts[0] == "lm":
                scene.list_maze = parts[1]
            elif parts[0] == "wl":
                scene.write_list_maze = bool(int(parts[1]))

            # tile settings
            elif parts[0] == "tb":
                scene.tile_based = bool(int(parts[1]))
            elif parts[0] == "im":
                scene.import_mat = bool(int(parts[1]))
            elif parts[0] == "mo":
                scene.merge_objects = bool(int(parts[1]))
            elif parts[0] == "am":
                scene.apply_modifiers = bool(int(parts[1]))
            elif parts[0] == "rd":
                scene.remove_doubles_merge = bool(int(parts[1]))

            # tile pieces
            elif parts[0] == "w0":
                scene.wall_0_sided = parts[1]
            elif parts[0] == "w1":
                scene.wall_1_sided = parts[1]
            elif parts[0] == "w2":
                scene.wall_2_sided = parts[1]
            elif parts[0] == "w3":
                scene.wall_3_sided = parts[1]
            elif parts[0] == "w4":
                scene.wall_4_sided = parts[1]
            elif parts[0] == "wc":
                scene.wall_corner = parts[1]
            elif parts[0] == "f0":
                scene.floor_0_sided = parts[1]
            elif parts[0] == "f1":
                scene.floor_1_sided = parts[1]
            elif parts[0] == "f2":
                scene.floor_2_sided = parts[1]
            elif parts[0] == "f3":
                scene.floor_3_sided = parts[1]
            elif parts[0] == "f4":
                scene.floor_4_sided = parts[1]
            elif parts[0] == "fc":
                scene.floor_corner = parts[1]

        return {'FINISHED'}


class DeleteBatchMazeMG(bpy.types.Operator):
    bl_label = "Delete Setting"
    bl_idname = "scene.delete_batch_maze"
    bl_description = "Deletes the maze settings for batch number."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        refresh_batch_max()

        if scene.num_batch_mazes == 0:
            self.report({'ERROR'}, "No mazes stored!")
            return {'CANCELLED'}

        if scene.batch_index > scene.num_batch_mazes:
            scene.batch_index = scene.num_batch_mazes
            self.report({'ERROR'}, "Not a maze index! Setting to highest " +
                        "batched maze number...")
            return {'CANCELLED'}

        # read text
        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)

        split_settings = settings_text.split(" && ")

        # delete setting
        del split_settings[scene.batch_index - 1]

        # create string
        new_settings_text = ""
        for i in split_settings:
            new_settings_text = new_settings_text + " && " + i

        # write out new text
        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "w") as s:
            s.write(new_settings_text)

        refresh_batch_max()

        return {'FINISHED'}


class BatchGenerateMazeMG(bpy.types.Operator):
    bl_label = "Batch Generate"
    bl_idname = "scene.batch_generate_maze"
    bl_description = "Generates a maze for each stored setting."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        my_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
        maze_setups_file = os.path.join(my_settings_dir, "maze_setups.txt")

        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)

        split_settings = settings_text.split(" && ")

        # check for if no mazes are stored
        if split_settings[0] == "":
            self.report({'ERROR'}, "No mazes stored! Click store settings to " +
                        "store current maze settings.")
            return {'CANCELLED'}

        time_start = time.time()
        for maze_setup in split_settings:

            maze_setup = maze_setup.split(";")

            for slot in maze_setup:
                parts = slot.split(",")

                # main settings
                if parts[0] == "wd":
                    scene.mg_width = int(parts[1])
                elif parts[0] == "ht":
                    scene.mg_height = int(parts[1])
                elif parts[0] == "3d":
                    scene.gen_3d_maze = bool(int(parts[1]))
                elif parts[0] == "al":
                    scene.allow_loops = bool(int(parts[1]))
                elif parts[0] == "lc":
                    scene.loops_chance = int(parts[1])
                elif parts[0] == "ai":
                    scene.allow_islands = bool(int(parts[1]))
                elif parts[0] == "fl":
                    scene.use_list_maze = bool(int(parts[1]))
                elif parts[0] == "lm":
                    scene.list_maze = parts[1]
                elif parts[0] == "wl":
                    scene.write_list_maze = bool(int(parts[1]))

                # tile settings
                elif parts[0] == "tb":
                    scene.tile_based = bool(int(parts[1]))
                elif parts[0] == "im":
                    scene.import_mat = bool(int(parts[1]))
                elif parts[0] == "mo":
                    scene.merge_objects = bool(int(parts[1]))
                elif parts[0] == "am":
                    scene.apply_modifiers = bool(int(parts[1]))
                elif parts[0] == "rd":
                    scene.remove_doubles_merge = bool(int(parts[1]))

                # tile pieces
                elif parts[0] == "w0":
                    scene.wall_0_sided = parts[1]
                elif parts[0] == "w1":
                    scene.wall_1_sided = parts[1]
                elif parts[0] == "w2":
                    scene.wall_2_sided = parts[1]
                elif parts[0] == "w3":
                    scene.wall_3_sided = parts[1]
                elif parts[0] == "w4":
                    scene.wall_4_sided = parts[1]
                elif parts[0] == "wc":
                    scene.wall_corner = parts[1]
                elif parts[0] == "f0":
                    scene.floor_0_sided = parts[1]
                elif parts[0] == "f1":
                    scene.floor_1_sided = parts[1]
                elif parts[0] == "f2":
                    scene.floor_2_sided = parts[1]
                elif parts[0] == "f3":
                    scene.floor_3_sided = parts[1]
                elif parts[0] == "f4":
                    scene.floor_4_sided = parts[1]
                elif parts[0] == "fc":
                    scene.floor_corner = parts[1]

            # GENERATE MAZE HERE

            if scene.tile_based and scene.gen_3d_maze:
                # if missing tiles: terminate operator
                if not prep_manager.check_tiles_exist():
                    self.report({'ERROR'}, "One or more tile objects is missing " +
                                "or is not a mesh! Please assign a valid object or " +
                                "disable 'Use Modeled Tiles'.")
                    return {'CANCELLED'}

            if scene.use_list_maze:
                # if missing list: terminate operator
                if not prep_manager.check_list_exist():
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
