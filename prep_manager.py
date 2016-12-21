"""Exist checks for required resources and complete file saving function.

Available functions:
    - check_tiles_exist: Check if all tile slots are filled in UI panel.
    - check_list_exist: Check if list is assigned in UI panel.
    - save_text: Saves Blender text block that is stored externally.
    - always_save: Saves .blend file and referenced images/texts.
"""

import bpy


def check_tiles_exist():
    """Check if all tile slots are filled in UI panel.

    Also sets tile slot to 'MISSING TILE' if not found.

    Returns:
        True if all tile slots are filled, otherwise, False
    """

    mg = bpy.context.scene.mg

    tiles_exist = True
    tiles_12 = [(mg.wall_4_sided, "mg.wall_4_sided"),
               (mg.wall_3_sided, "mg.wall_3_sided"),
               (mg.wall_2_sided, "mg.wall_2_sided"),
               (mg.wall_1_sided, "mg.wall_1_sided"),
               (mg.wall_0_sided, "mg.wall_0_sided"),
               (mg.wall_corner, "mg.wall_corner"),
               (mg.floor_4_sided, "mg.floor_4_sided"),
               (mg.floor_3_sided, "mg.floor_3_sided"),
               (mg.floor_2_sided, "mg.floor_2_sided"),
               (mg.floor_1_sided, "mg.floor_1_sided"),
               (mg.floor_0_sided, "mg.floor_0_sided"),
               (mg.floor_corner, "mg.floor_corner")]

    tiles_6 = [(mg.four_way, "mg.four_way"),
               (mg.t_int, "mg.t_int"),
               (mg.turn, "mg.turn"),
               (mg.dead_end, "mg.dead_end"),
               (mg.straight, "mg.straight"),
               (mg.no_path, "mg.no_path")]

    if mg.tile_mode == 'SIX_TILES':
        for tile in tiles_6:
            try:
                object_type = bpy.data.objects[tile[0]].type
                if object_type != 'MESH':
                    tiles_exist = False
                    exec(tile[1] + "= 'MISSING TILE'")
            except KeyError:
                tiles_exist = False
                exec(tile[1] + "= 'MISSING TILE'")

    elif mg.tile_mode == 'TWELVE_TILES':
        for tile in tiles_12:
            try:
                object_type = bpy.data.objects[tile[0]].type
                if object_type != 'MESH':
                    tiles_exist = False
                    exec(tile[1] + "= 'MISSING TILE'")
            except KeyError:
                tiles_exist = False
                exec(tile[1] + "= 'MISSING TILE'")

    return tiles_exist


def check_list_exist():
    """Check if list is assigned in UI panel.

    Returns:
        True if list is assigned, otherwise, False
    """
    list_exist = True

    try:
        bpy.data.texts[bpy.context.scene.mg.list_maze]
    except KeyError:
        list_exist = False

    return list_exist


def save_text(text):
    """Saves Blender text block that is stored externally.

    Args:
        text: Blender text block to save.
    """
    # get filepath and text
    text_path = text.filepath
    text_as_string = text.as_string()
    # write to file
    with open(text_path, "w") as d:
        d.write(str(text_as_string))


def always_save():
    """Saves .blend file and referenced images/texts.

    Does not save 'Render Result' or 'Viewer Node'

    Returns:
        "BLEND_ERROR", None: IF file has not been saved (no filepath)
        "IMAGE_ERROR", image: IF image has not been saved
        "SUCCESS", None: IF saved all required types correctly
    """

    addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences
    debug = addon_prefs.debug_mode

    # save file
    if addon_prefs.always_save_prior:
        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile()
            if not debug:
                print("File saved...")
        else:
            return "BLEND_ERROR", None

    # save all images
    if addon_prefs.save_all_images:
        for image in bpy.data.images:
            if image.has_data:
                if not image.packed_file:
                    if not image.filepath:
                        if image.name != 'Render Result' and image.name != 'Viewer Node':
                            return "IMAGE_ERROR", image
                    else:
                        image.save()

    # save all texts
    if addon_prefs.save_all_texts:
        for text in bpy.data.texts:
            if text.filepath and text.is_dirty:
                # my function for saving texts
                save_text(text)
    return "SUCCESS", None
