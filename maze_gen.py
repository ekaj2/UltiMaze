from time import time

import bpy

from maze_gen import prep_manager
from maze_gen import txt_img_converter
from maze_gen import auto_layout_gen
from maze_gen import tile_maze_gen
from maze_gen import time_log
from maze_gen.bmesh_maze_gen import Make3DMaze
from maze_gen.time_display import TimeDisplay


def morph_dimensions():
    mg = bpy.context.scene.mg
    if not mg.mg_width & 1:
        mg.mg_width += 1
    if not mg.mg_height & 1:
        mg.mg_height += 1


def make_maze(context):
    """
    Makes a maze based on the settings specified in the UI.

    Args:
        context: context of the operator

    Returns:
        message: message to print to user
        message_lvl: level to print message as, 'INFO', 'WARNING', 'ERROR'
        status: whether operator is 'FINISHED', 'CANCELLED', or other status
    """
    addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences

    messages = []
    message_lvls = []
    mg = context.scene.mg
    time_start = time()

    # check that all needed tiles and lists have been provided
    if mg.tile_based and mg.gen_3d_maze:
        tiles_exist = prep_manager.check_tiles_exist()
        # if missing tiles: terminate operator
        if not tiles_exist:
            messages += ["One or more tile objects is missing " + "or is not a mesh! Please assign a valid object or " + "disable 'Use Modeled Tiles'."]
            message_lvls += ['ERROR']
            return messages, message_lvls, 'CANCELLED'

    if mg.use_list_maze:
        list_exist = prep_manager.check_list_exist()
        # if missing list: terminate operator
        if not list_exist:
            messages += ["List missing! Please assign a valid " + "text data block or disable 'Generate Maze From List'."]
            message_lvls += ['ERROR']
            return messages, message_lvls, 'CANCELLED'

    # save files
    save_return, bad_file = prep_manager.always_save()
    if save_return == "BLEND_ERROR":
        messages += ["Save file or disable always save " + "in user prefs."]
        message_lvls += ['ERROR']
        return messages, message_lvls, 'CANCELLED'

    elif save_return == "IMAGE_ERROR":
        messages += ["Image '" + bad_file.name + "' does not have a valid file path (for saving). Assign " + "a valid path, pack image, or disable save images in " + "user prefs"]
        message_lvls += ['ERROR']
        return messages, message_lvls, 'CANCELLED'

    elif save_return == "TEXT_ERROR":
        messages += ["Text '" + bad_file.name + "' does not have a valid file path (for saving). " + "Assign a valid path or disable save texts in user prefs"]
        message_lvls += ['ERROR']
        return messages, message_lvls, 'CANCELLED'

    if mg.gen_3d_maze or mg.write_list_maze:
        if addon_prefs.only_odd_sizes:
            morph_dimensions()
        if mg.use_list_maze:
            maze = txt_img_converter.convert_list_maze()
        else:
            maze = auto_layout_gen.make_list_maze()

        if mg.allow_loops:
            maze = auto_layout_gen.add_loops(maze)

        # 3D generation
        if mg.gen_3d_maze:
            bpy.ops.object.select_all(action='DESELECT')
            if mg.tile_based:
                tile_maze_gen.make_tile_maze(maze)
            else:
                Make3DMaze(maze)

            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        elapsed_time = time() - time_start
        time_log.log_time(elapsed_time)
        time_disp = TimeDisplay()
        time_disp.convert(elapsed_time)
        messages += ["Finished generating maze in " + str(time_disp)]
        message_lvls += ['INFO']

        # write list maze if enabled
        if mg.write_list_maze:
            text_block_name = txt_img_converter.str_list_maze(maze)
            messages += ["See '" + str(text_block_name) + "' in the text editor"]
            message_lvls += ['INFO']

    return messages, message_lvls, 'FINISHED'
