import time

from maze_gen import prep_manager
from maze_gen import txt_img_converter
from maze_gen import auto_layout_gen
from maze_gen import tile_maze_gen
from maze_gen import simple_maze_gen
from maze_gen import time_log


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
    messages = []
    message_lvls = []
    scene = context.scene
    time_start = time.time()

    # check that all needed tiles and lists have been provided
    if scene.tile_based and scene.gen_3d_maze:
        tiles_exist = prep_manager.check_tiles_exist()
        # if missing tiles: terminate operator
        if not tiles_exist:
            messages += ["One or more tile objects is missing " + "or is not a mesh! Please assign a valid object or " + "disable 'Use Modeled Tiles'."]
            message_lvls += ['ERROR']
            return messages, message_lvls, 'CANCELLED'

    if scene.use_list_maze:
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

    apply_mods = scene.apply_modifiers
    if not scene.merge_objects:
        # fix to make sure not applying modifiers
        # if merging is disabled (because group is not made)
        scene.apply_modifiers = False

    if scene.use_list_maze:
        maze = txt_img_converter.convert_list_maze()
    elif scene.gen_3d_maze or scene.write_list_maze:
        maze = auto_layout_gen.make_list_maze()

    if scene.allow_loops:
        maze = auto_layout_gen.add_loops(maze)

    # 3D generation
    if scene.gen_3d_maze:
        if scene.tile_based:
            tile_maze_gen.make_tile_maze(maze)
        else:
            simple_maze_gen.make_3dmaze(maze)

    scene.apply_modifiers = apply_mods

    if scene.gen_3d_maze or scene.write_list_maze:
        time_log.log_time(time.time() - time_start)
        messages += ["Finished generating maze in " + str(time.time() - time_start) + " seconds"]
        message_lvls += ['INFO']

    # write list maze if enabled
    if scene.write_list_maze:
        text_block_name = txt_img_converter.str_list_maze(maze)
        messages += ["See '" + str(text_block_name) + "' in the text editor"]
        message_lvls += ['INFO']

    return messages, message_lvls, 'FINISHED'
