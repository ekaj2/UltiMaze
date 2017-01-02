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
Batch tools for mazes

Available Functions:
    refresh_batch_max - Refreshes number of batch mazes by checking txt file
"""

import os

import bpy

from . import maze_gen
from . import menus


def refresh_batch_max():
    """Refreshes number of batch mazes by checking txt file."""
    maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

    with open(maze_setups_file, "r") as s:
        settings_text = s.read()

    settings_text = settings_text.replace(" && ", "", 1)

    split_settings = settings_text.split(" && ")

    if settings_text == "":
        bpy.context.scene.mg.num_batch_mazes = 0
    else:
        bpy.context.scene.mg.num_batch_mazes = len(split_settings)


def load_batch_settings(context, maze_setup):
    scene = context.scene
    mg = scene.mg
    for slot in maze_setup:
        parts = slot.split(",")

        # main settings
        if parts[0] == "wd":
            mg.mg_width = int(parts[1])
        elif parts[0] == "ht":
            mg.mg_height = int(parts[1])
        elif parts[0] == "3d":
            mg.gen_3d_maze = bool(int(parts[1]))
        elif parts[0] == "al":
            mg.allow_loops = bool(int(parts[1]))
        elif parts[0] == "lc":
            mg.loops_chance = int(parts[1])
        elif parts[0] == "fl":
            mg.use_list_maze = bool(int(parts[1]))
        elif parts[0] == "lm":
            mg.list_maze = parts[1]
        elif parts[0] == "wl":
            mg.write_list_maze = bool(int(parts[1]))

        # algorithm settings
        elif parts[0] == 'ag':
            mg.algorithm = parts[1]
        elif parts[0] == 'br':
            mg.bias_direction = parts[1]
        elif parts[0] == 'bd':
            mg.binary_dir = parts[1]
        elif parts[0] == 'ti':
            mg.tileable = bool(int(parts[1]))
        elif parts[0] == 'bi':
            mg.bias = float(parts[1])

        # tile settings
        elif parts[0] == "tb":
            mg.tile_based = bool(int(parts[1]))
        elif parts[0] == "im":
            mg.import_mat = bool(int(parts[1]))
        elif parts[0] == "mo":
            mg.merge_objects = bool(int(parts[1]))
        elif parts[0] == "am":
            mg.apply_modifiers = bool(int(parts[1]))
        elif parts[0] == "rd":
            mg.remove_doubles_merge = bool(int(parts[1]))
        elif parts[0] == "tm":
            mg.tile_mode = parts[1]

        # 12 tile pieces
        elif parts[0] == "w0":
            mg.wall_0_sided = parts[1]
        elif parts[0] == "w1":
            mg.wall_1_sided = parts[1]
        elif parts[0] == "w2":
            mg.wall_2_sided = parts[1]
        elif parts[0] == "w3":
            mg.wall_3_sided = parts[1]
        elif parts[0] == "w4":
            mg.wall_4_sided = parts[1]
        elif parts[0] == "wc":
            mg.wall_corner = parts[1]
        elif parts[0] == "f0":
            mg.floor_0_sided = parts[1]
        elif parts[0] == "f1":
            mg.floor_1_sided = parts[1]
        elif parts[0] == "f2":
            mg.floor_2_sided = parts[1]
        elif parts[0] == "f3":
            mg.floor_3_sided = parts[1]
        elif parts[0] == "f4":
            mg.floor_4_sided = parts[1]
        elif parts[0] == "fc":
            mg.floor_corner = parts[1]

        # 6 tile pieces
        elif parts[0] == "4w":
            mg.four_way = parts[1]
        elif parts[0] == "3w":
            mg.t_int = parts[1]
        elif parts[0] == "2t":
            mg.turn = parts[1]
        elif parts[0] == "de":
            mg.dead_end = parts[1]
        elif parts[0] == "2s":
            mg.straight = parts[1]
        elif parts[0] == "np":
            mg.no_path = parts[1]


class StoreBatchMazeMG(bpy.types.Operator):
    bl_label = "Store Settings"
    bl_idname = "maze_gen.store_batch_maze"
    bl_description = "Stores a maze to batch generate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mg = context.scene.mg
        settings_text = (" && wd,{};ht,{};3d,{};al,{};lc,{};"
                         "fl,{};lm,{};wl,{};"
                         "ag,{};br,{};bd,{};ti,{};bi,{};"
                         "tb,{};im,{};mo,{};am,{};rd,{};"
                         "w0,{};w1,{};w2,{};w3,{};w4,{};wc,{};"
                         "f0,{};f1,{};f2,{};f3,{};f4,{};fc,{};"
                         "tm,{};4w,{};3w,{};2t,{};de,{};2s,{};np,{}".format(
                            mg.mg_width,
                            mg.mg_height,
                            int(mg.gen_3d_maze),
                            int(mg.allow_loops),
                            mg.loops_chance,
                            int(mg.use_list_maze),
                            mg.list_maze,
                            int(mg.write_list_maze),
                            mg.algorithm,
                            mg.bias_direction,
                            mg.binary_dir,
                            int(mg.tileable),
                            mg.bias,
                            int(mg.tile_based),
                            int(mg.import_mat),
                            int(mg.merge_objects),
                            int(mg.apply_modifiers),
                            int(mg.remove_doubles_merge),
                            mg.wall_0_sided,
                            mg.wall_1_sided,
                            mg.wall_2_sided,
                            mg.wall_3_sided,
                            mg.wall_4_sided,
                            mg.wall_corner,
                            mg.floor_0_sided,
                            mg.floor_1_sided,
                            mg.floor_2_sided,
                            mg.floor_3_sided,
                            mg.floor_4_sided,
                            mg.floor_corner,
                            mg.tile_mode,
                            mg.four_way,
                            mg.t_int,
                            mg.turn,
                            mg.dead_end,
                            mg.straight,
                            mg.no_path))

        maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

        with open(maze_setups_file, "a") as s:
            print(settings_text, end="", file=s, flush=True)

        mg.num_batch_mazes += 1

        return {'FINISHED'}


class ClearBatchMazesMG(bpy.types.Operator):
    bl_label = "Clear Mazes"
    bl_idname = "maze_gen.clear_batch_maze"
    bl_description = "Clears all mazes from batch cache."
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        mg = context.scene.mg

        maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

        with open(maze_setups_file, "w") as s:
            s.write("")

        mg.num_batch_mazes = 0

        return {'FINISHED'}


class RefreshBatchMazesMG(bpy.types.Operator):
    bl_label = "Refresh"
    bl_idname = "maze_gen.refresh_batch_num"
    bl_description = "Refreshes number of batches."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_batch_max()
        return {'FINISHED'}


class LoadBatchMazeMG(bpy.types.Operator):
    bl_label = "Load Settings"
    bl_idname = "maze_gen.load_batch_maze"
    bl_description = "Loads the maze settings for batch number."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mg = context.scene.mg

        refresh_batch_max()

        if mg.num_batch_mazes == 0:
            self.report({'ERROR'}, "No mazes stored!")
            return {'CANCELLED'}

        if mg.batch_index > mg.num_batch_mazes:
            mg.batch_index = mg.num_batch_mazes
            self.report({'ERROR'}, "Not a maze index! Setting to highest " +
                        "batched maze number...")
            return {'CANCELLED'}

        maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)

        split_settings = settings_text.split(" && ")

        maze_setup = split_settings[mg.batch_index - 1]

        maze_setup = maze_setup.split(";")

        load_batch_settings(context, maze_setup)

        return {'FINISHED'}


class DeleteBatchMazeMG(bpy.types.Operator):
    bl_label = "Delete Setting"
    bl_idname = "maze_gen.delete_batch_maze"
    bl_description = "Deletes the maze settings for batch number."
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        mg = context.scene.mg

        refresh_batch_max()

        if mg.num_batch_mazes == 0:
            self.report({'ERROR'}, "No mazes stored!")
            return {'CANCELLED'}

        if mg.batch_index > mg.num_batch_mazes:
            mg.batch_index = mg.num_batch_mazes
            self.report({'ERROR'}, "Not a maze index! Setting to highest " +
                        "batched maze number...")
            return {'CANCELLED'}

        maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

        # read text
        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)
        split_settings = settings_text.split(" && ")
        # delete setting
        del split_settings[mg.batch_index - 1]

        # create string
        new_settings_text = ""
        for i in split_settings:
            new_settings_text = new_settings_text + " && " + i

        # write out new text
        with open(maze_setups_file, "w") as s:
            s.write(new_settings_text)

        refresh_batch_max()

        return {'FINISHED'}


class BatchGenerateMazeMG(bpy.types.Operator):
    bl_label = "Batch Generate"
    bl_idname = "maze_gen.batch_generate_maze"
    bl_description = "Generates a maze for each stored setting."
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene

        if not scene.layers[0]:
            bpy.ops.wm.call_menu(name=menus.EnableLayerMenu.bl_idname)
            return {'CANCELLED'}

        maze_setups_file = os.path.join(os.path.dirname(__file__), "settings", "maze_setups.txt")

        with open(maze_setups_file, "r") as s:
            settings_text = s.read()

        settings_text = settings_text.replace(" && ", "", 1)
        split_settings = settings_text.split(" && ")
        # check for if no mazes are stored
        if split_settings[0] == "":
            self.report({'ERROR'}, "No mazes stored! Click store settings to " +
                        "store current maze settings.")
            return {'CANCELLED'}

        for maze_setup in split_settings:
            maze_setup = maze_setup.split(";")
            load_batch_settings(context, maze_setup)

            # generate maze here...ignore the status unless it is cancelled
            messages, message_lvls, status = maze_gen.make_maze(context)
            for i, message in enumerate(messages):
                self.report({message_lvls[i]}, message)
            if status == 'CANCELLED':
                return {status}

        return {'FINISHED'}
