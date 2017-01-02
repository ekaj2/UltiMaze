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
Converts back and forth between image and text mazes.

Available Functions:
    console_prog - Displays progress in the console
    write_to_text - Writes text to Blender text file with current width and
                    height settings
    write_to_text_img - Writes text to Blender text file with given width and
                        height
    str_list_maze - Converts a python maze into a text block
    convert_list_maze - Convert text maze into a Python list maze
"""
import logging

import bpy

from . import prep_manager
from .maze_tools import Maze
from .progress_display import BlenderProgress
from .time_display import TimeDisplay
from .logging_setup import setup_logger
from .addon_name import get_addon_name

setup_logger(__name__)


def write_to_text(text):
    """Writes text to Blender text file with current width and height settings.

    Args:
        text - text to write

    Returns:
        actual name of text block it wrote to
    """
    width = bpy.context.scene.mg.mg_width
    height = bpy.context.scene.mg.mg_height

    attempted_name = (str(width) + "x" + str(height) + "_maze_list")

    text_block = [""]
    text_data_block = bpy.data.texts.new(name=attempted_name)
    text_block[0] = text_data_block

    text_block[0].from_string(str(text))

    text_block_name = text_block[0].name

    return text_block_name


def write_to_text_img(text, width, height):
    """Writes text to Blender text file with given width and height.

    Args:
        text - text to write
        width - width of 'maze'
        height - height of 'maze'

    Returns:
        actual name of text block it wrote to
    """
    attempted_name = (str(width) + "x" + str(height) + "_maze_list")

    text_block = [""]
    text_data_block = bpy.data.texts.new(name=attempted_name)
    text_block[0] = text_data_block

    text_block[0].from_string(text)

    text_block_name = text_block[0].name

    return text_block_name


def str_list_maze(maze):
    """Converts a python maze into a text block.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]

    Returns:
        actual name of text block it wrote to
    """
    str_maze = ""
    for row in range(maze.height):
        for column in range(maze.width):
            if maze.is_path(column, row):
                str_maze += "1"
            else:
                str_maze += "0"

    text_block_name = write_to_text(str_maze)

    return text_block_name


def convert_list_maze():
    """Convert text maze into a Python list maze.

    Returns:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """

    mg = bpy.context.scene.mg
    list_maze = mg.list_maze
    str_maze = bpy.data.texts[list_maze].as_string()

    # replace "\n" with ""
    str_maze = str_maze.replace("\n", "")

    x_dim = mg.mg_width
    y_dim = mg.mg_height

    maze = Maze(x_dim, y_dim)
    for y in range(maze.height):
        for x in range(maze.width):
            index = y * maze.width + x
            try:
                if str_maze[index] == "1":
                    maze.make_path(x, y)
            except IndexError:
                logging.getLogger(__name__).warning("IndexError when trying to access a text file's string for "
                                                    "converting to a list maze..."
                                                    "index={}, maze.width={}, maze.height={}".format(index,
                                                                                                     maze.width,
                                                                                                     maze.height))

    return maze


class ConvertMazeImageMG(bpy.types.Operator):
    bl_label = "Image to Text"
    bl_idname = "maze_gen.convert_maze_image"
    bl_description = "Creates a textblock with maze generated from image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mg = context.scene.mg
        logger = logging.getLogger(__name__)

        # check if image is assigned
        if not mg.maze_image:
            logger.debug("Image missing! Please assign a valid image data block.")
            self.report({'ERROR'}, "Image missing! Please assign a valid image data block.")
            return {'CANCELLED'}

        # save files
        save_return, bad_file = prep_manager.always_save()
        if save_return == "BLEND_ERROR":
            logger.debug("Save file or disable always save in user prefs.")
            self.report({'ERROR'}, "Save file or disable always save in user prefs.")
            return {'CANCELLED'}

        elif save_return == "IMAGE_ERROR":
            logger.debug("Image: {} does not have a valid file path (for saving). Assign a valid path, "
                         "pack img, or disable save images in user prefs".format(bad_file.name))
            self.report({'ERROR'}, "Image '" + bad_file.name +
                        "' does not have a valid file path (for saving). Assign a "
                        "valid path, pack image, or disable save images in user prefs")
            return {'CANCELLED'}

        elif save_return == "TEXT_ERROR":
            logger.debug("Text: {} does not have a valid file path (for saving). Assign a valid path,"
                         "or disable save texts in user prefs".format(bad_file.name))
            self.report({'ERROR'}, "Text '" + bad_file.name +
                        "' does not have a valid file path (for saving). Assign a " +
                        "valid path or disable save texts in user prefs")
            return {'CANCELLED'}

        x_dim = bpy.data.images[mg.maze_image].size[0]
        y_dim = bpy.data.images[mg.maze_image].size[1]

        maze = ""

        count = 0
        while count < len(bpy.data.images[mg.maze_image].pixels):

            # if value is white, its a path, otherwise a wall
            if bpy.data.images[mg.maze_image].pixels[count] > 0.5:
                maze += "1"
            else:
                maze += "0"

            # if image has alpha channel...
            # this actually seems to work without alpha channel :(
            count += 4

        # the maze at this point is a mirror of what it should be
        flipped_maze = ""
        row = (y_dim - 1)
        while row >= 0:
            # snippet from exist test (here for reference only)
            #            index = (x + (y * (x_dimensions)))

            maze_row = maze[(row * x_dim):(row * x_dim + x_dim)]
            flipped_maze += maze_row

            row -= 1

        text_block_name = write_to_text_img(flipped_maze, x_dim, y_dim)

        self.report({'INFO'}, "See '" + str(text_block_name) +
                    "' in the text editor")

        return {'FINISHED'}


class CreateImageFromListMG(bpy.types.Operator):
    bl_label = "Text to Image"
    bl_idname = "maze_gen.create_image_from_list"
    bl_description = "Creates an image with maze generated from textblock"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        debug = bpy.context.user_preferences.addons[get_addon_name()].preferences.debug_mode
        mg = context.scene.mg

        if not mg.list_maze:
            self.report({'ERROR'}, "List missing! Please assign a " +
                        "valid text data block.")
            return {'CANCELLED'}

        # save files
        save_return, bad_file = prep_manager.always_save()
        if save_return == "BLEND_ERROR":
            self.report({'ERROR'}, "Save file or disable always save " +
                        "in user prefs.")
            return {'CANCELLED'}

        elif save_return == "IMAGE_ERROR":
            self.report({'ERROR'}, "Image '" + bad_file.name +
                        "' does not have a valid file path (for saving). Assign a " +
                        "valid path, pack image, or disable save images in user prefs")
            return {'CANCELLED'}

        elif save_return == "TEXT_ERROR":
            self.report({'ERROR'}, "Text '" + bad_file.name +
                        "' does not have a valid file path (for saving). Assign a " +
                        "valid path or disable save texts in user prefs")
            return {'CANCELLED'}

        bldr_prog = BlenderProgress("Text to Image", debug)
        bldr_prog.start()

        # get list maze as string
        str_list_maze = bpy.data.texts[mg.list_maze].as_string()

        # settings check before execution
        area = mg.mg_width * mg.mg_height
        if len(str_list_maze) != area:
            self.report({'ERROR'}, "Width and Height settings don't match " +
                        "selected textblock! Width x Height should equal the number " +
                        "of characters in text.")
            return {'CANCELLED'}

        # create image
        image_maze = bpy.data.images.new(
            name="Maze",
            width=mg.mg_width,
            height=mg.mg_height)

        image_row = mg.mg_height - 1
        count = 0
        while image_row >= 0:
            image_col = 0
            while image_col < mg.mg_width:
                if str_list_maze[count] == "1":
                    # Red Channel
                    image_maze.pixels[(image_row * mg.mg_width * 4 +
                                       image_col * 4 + 0)] = 1
                    # Green Channel
                    image_maze.pixels[(image_row * mg.mg_width * 4 +
                                       image_col * 4 + 1)] = 1
                    # Blue Channel
                    image_maze.pixels[(image_row * mg.mg_width * 4 +
                                       image_col * 4 + 2)] = 1
                    # Alpha Channel
                    image_maze.pixels[(image_row * mg.mg_width * 4 +
                                       image_col * 4 + 3)] = 1

                # report progress if changed
                progress = count / area
                bldr_prog.update(progress)

                image_col += 1
                count += 1
            image_row -= 1

        bldr_prog.finish()
        time_disp = TimeDisplay()
        time_disp.convert(bldr_prog.elapsed_time())

        self.report({'INFO'}, "Finished generating 2d maze in " + str(time_disp))

        self.report({'INFO'}, "See '" + image_maze.name +
                    "' in the image editor")

        return {'FINISHED'}
