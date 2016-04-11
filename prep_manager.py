"""Exist checks for required resources and complete file saving function.

Available functions:
    - check_tiles_exist: Check if all tile slots are filled in UI panel.
    - check_list_exist: Check if list is assigned in UI panel.
    - save_text: Saves Blender text block that is stored externally.
    - always_save: Saves .blend file and referenced images/texts.
"""

import os

import bpy


def check_tiles_exist():
    """Check if all tile slots are filled in UI panel.
    
    Returns:
        True if all tile slots are filled, otherwise, False
    """
    
    tiles_exist = True
    tiles = [bpy.context.scene.wall_4_sided,
             bpy.context.scene.wall_3_sided,
             bpy.context.scene.wall_2_sided,
             bpy.context.scene.wall_1_sided,
             bpy.context.scene.wall_0_sided,
             bpy.context.scene.wall_corner,
             bpy.context.scene.floor_4_sided,
             bpy.context.scene.floor_3_sided,
             bpy.context.scene.floor_2_sided,
             bpy.context.scene.floor_1_sided,
             bpy.context.scene.floor_0_sided,
             bpy.context.scene.floor_corner]

    for tile in tiles:
        try:
            object_type = bpy.data.objects[tile].type
            if object_type != 'MESH':
                tiles_exist = False
        except KeyError:
            tiles_exist = False
        
    return tiles_exist


def check_list_exist():
    """Check if list is assigned in UI panel.
    
    Returns:
        True if list is assigned, otherwise, False
    """
    list_exist = True

    try:
        bpy.data.texts[bpy.context.scene.list_maze]
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
    disk_file = open(text_path, "w")
    disk_file.write(str(text_as_string))
    disk_file.close()


def always_save():
    """Saves .blend file and referenced images/texts.
    
    Does not save 'Render Result' or 'Viewer Node'
        
    Returns:
        "BLEND_ERROR", None: IF file has not been saved (no filepath)
        "IMAGE_ERROR", image: IF image has not been saved
        "SUCCESS", None: IF saved all required types correctly
    """
    wm = bpy.context.window_manager
    scene = bpy.context.scene
    
    addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences
    
    # save file
    if addon_prefs.always_save_prior:
        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile()
            print("File saved...")
        else:
            return "BLEND_ERROR", None

    # save all images
    if addon_prefs.save_all_images:
        for image in bpy.data.images:
            if not image.packed_file:
                if not image.filepath:
                    if (image.name != 'Render Result' and 
                        image.name != 'Viewer Node'):
                            
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