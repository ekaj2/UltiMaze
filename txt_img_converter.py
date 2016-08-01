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

import bpy
from maze_gen import prep_manager

from maze_gen.progress_display import BlenderProgress


def write_to_text(text):
    """Writes text to Blender text file with current width and height settings.

    Args:
        text - text to write

    Returns:
        actual name of text block it wrote to
    """
    width = bpy.context.scene.mg_width
    height = bpy.context.scene.mg_height

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
    for i, space in enumerate(maze):
        if maze[i][1]:
            new_space = "1"
            old_str_maze = str_maze
            str_maze = old_str_maze + new_space
        else:
            new_space = "0"
            old_str_maze = str_maze
            str_maze = old_str_maze + new_space

    text_block_name = write_to_text(str_maze)

    return text_block_name


def convert_list_maze():
    """Convert text maze into a Python list maze.

    Returns:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    list_maze = bpy.context.scene.list_maze
    str_list_maze = bpy.data.texts[list_maze].as_string()

    # replace "\n" with ""
    str_list_maze = str_list_maze.replace("\n", "")

    x_dim = bpy.context.scene.mg_width
    y_dim = bpy.context.scene.mg_height

    maze = []
    for y in range(0, y_dim):
        for x in range(0, x_dim):
            # [[space in maze(ordered pair),is path,is walkable,active path]]
            maze_addition = [[(x, y), False]]
            maze += maze_addition

    index = 0
    for space in maze:
        # if nothing in list make all false, if list
        # runs out use last element in list for the rest
        if len(str_list_maze) > 0:
            if str_list_maze[index] == "1":
                space[1] = True
            else:
                space[1] = False
        else:
            space[1] = False

        if index < (len(str_list_maze) - 1):
            index += 1

    return maze


class ConvertMazeImageMG(bpy.types.Operator):
    bl_label = "Image to Text"
    bl_idname = "maze_gen.convert_maze_image"
    bl_description = "Creates a textblock with maze generated from image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # check if image is assigned
        if not scene.maze_image:
            self.report({'ERROR'}, "Image missing! Please assign a " +
                        "valid image data block.")
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

        x_dim = bpy.data.images[scene.maze_image].size[0]
        y_dim = bpy.data.images[scene.maze_image].size[1]

        maze = ""

        count = 0
        while count < len(bpy.data.images[scene.maze_image].pixels):

            # if value is white, its a path, otherwise a wall
            if bpy.data.images[scene.maze_image].pixels[count] > 0.5:
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
        debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode
        scene = context.scene

        if not scene.list_maze:
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
        str_list_maze = bpy.data.texts[scene.list_maze].as_string()

        # settings check before execution
        area = scene.mg_width * scene.mg_height
        if len(str_list_maze) != area:
            self.report({'ERROR'}, "Width and Height settings don't match " +
                        "selected textblock! Width x Height should equal the number " +
                        "of characters in text.")
            return {'CANCELLED'}

        # create image
        image_maze = bpy.data.images.new(
            name="Maze",
            width=scene.mg_width,
            height=scene.mg_height)

        image_row = scene.mg_height - 1
        count = 0
        while image_row >= 0:
            image_col = 0
            while image_col < scene.mg_width:
                if str_list_maze[count] == "1":
                    # Red Channel
                    image_maze.pixels[(image_row * scene.mg_width * 4 +
                                       image_col * 4 + 0)] = 1
                    # Green Channel
                    image_maze.pixels[(image_row * scene.mg_width * 4 +
                                       image_col * 4 + 1)] = 1
                    # Blue Channel
                    image_maze.pixels[(image_row * scene.mg_width * 4 +
                                       image_col * 4 + 2)] = 1
                    # Alpha Channel
                    image_maze.pixels[(image_row * scene.mg_width * 4 +
                                       image_col * 4 + 3)] = 1

                # report progress if changed
                progress = count / area
                bldr_prog.update(progress)

                image_col += 1
                count += 1
            image_row -= 1

        bldr_prog.finish()

        self.report({'INFO'}, "Finished generating 2d maze in " +
                    str(bldr_prog.elapsed()) + " seconds")

        self.report({'INFO'}, "See '" + image_maze.name +
                    "' in the image editor")

        return {'FINISHED'}
