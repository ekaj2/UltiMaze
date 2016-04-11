"""
Tile-based maze generation.

Available Functions:
    console_prog - Displays progress in the console
    add_tile - Adds a tile object to the scene at certain transform
    choose_tile - Chooses what tile to add based on surrounding spaces in maze
    make_tile_maze - Makes tile-based maze
"""

import math
import sys
from time import time

import bpy

from maze_gen import auto_layout_gen


def console_prog(job, progress, total_time="?"):
    """Displays progress in the console.
    
    Args:
        job - name of the job
        progress - progress as a decimal number
        total_time (optional) - the total amt of time the job 
                                took for final display
    """
    length = 20
    block = int(round(length*progress))
    message = "\r{0}: [{1}{2}] {3:.0%}".format(job, "#"*block, "-"*(length-block), progress)
    # progress is complete
    if progress >= 1:
        message = "\r{} DONE IN {} SECONDS{}".format(job.upper(), total_time, " "*12)
    sys.stdout.write(message)
    sys.stdout.flush()


def add_tile(tile, location, rotation):
    """Adds a tile object to the scene at certain transform.
    
    Args:
        tile - tile to add
        location - location component of desired transform
        rotation - rotation component of desired transform
    """
    x_transform = location[0]
    y_transform = location[1]
    
    # setup tiles for reference
    wall_4_sided = bpy.context.scene.wall_4_sided
    wall_3_sided = bpy.context.scene.wall_3_sided
    wall_2_sided = bpy.context.scene.wall_2_sided
    wall_1_sided = bpy.context.scene.wall_1_sided
    wall_0_sided = bpy.context.scene.wall_0_sided
    wall_corner = bpy.context.scene.wall_corner
    floor_4_sided = bpy.context.scene.floor_4_sided
    floor_3_sided = bpy.context.scene.floor_3_sided
    floor_2_sided = bpy.context.scene.floor_2_sided
    floor_1_sided = bpy.context.scene.floor_1_sided
    floor_0_sided = bpy.context.scene.floor_0_sided
    floor_corner = bpy.context.scene.floor_corner

    # clear selection
    bpy.ops.object.select_all(action='DESELECT')

    # select object correct tile
    if tile == 'wall_4_sided':
        bpy.data.objects[wall_4_sided].select = True
    elif tile == 'wall_3_sided':
        bpy.data.objects[wall_3_sided].select = True
    elif tile == 'wall_2_sided':
        bpy.data.objects[wall_2_sided].select = True
    elif tile == 'wall_1_sided':
        bpy.data.objects[wall_1_sided].select = True
    elif tile == 'wall_0_sided':
        bpy.data.objects[wall_0_sided].select = True
    elif tile == 'wall_corner':
        bpy.data.objects[wall_corner].select = True
    elif tile == 'floor_4_sided':
        bpy.data.objects[floor_4_sided].select = True
    elif tile == 'floor_3_sided':
        bpy.data.objects[floor_3_sided].select = True
    elif tile == 'floor_2_sided':
        bpy.data.objects[floor_2_sided].select = True
    elif tile == 'floor_1_sided':
        bpy.data.objects[floor_1_sided].select = True
    elif tile == 'floor_0_sided':
        bpy.data.objects[floor_0_sided].select = True
    elif tile == 'floor_corner':
        bpy.data.objects[floor_corner].select = True

    # ensure there is an active object
    bpy.context.scene.objects.active = bpy.context.selected_objects[0]

    # select children
    bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

    # duplicate and move
    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, 
        TRANSFORM_OT_translate={"value":(0, 0, 0), 
        "constraint_axis":(False, False, False), 
        "constraint_orientation":'GLOBAL', 
        "mirror":False, 
        "proportional":'DISABLED', 
        "proportional_edit_falloff":'SMOOTH', 
        "proportional_size":1, 
        "snap":False, 
        "snap_target":'CLOSEST', 
        "snap_point":(0, 0, 0), 
        "snap_align":False, 
        "snap_normal":(0, 0, 0), 
        "gpencil_strokes":False, 
        "texture_space":False, 
        "remove_on_cancel":False, 
        "release_confirm":False})

    tile_parent = bpy.context.scene.objects.active
        
    tile_parent.location[0] = x_transform
    tile_parent.location[1] = -y_transform
    tile_parent.rotation_euler[2] = math.radians(rotation)
    
    if bpy.context.scene.merge_objects:
        # add to group MazeGenerator
        for active in bpy.context.selected_objects:
            bpy.context.scene.objects.active = active
            try:
                bpy.ops.object.group_link(group='MazeGeneratorDoNotTouch')
            except:
                bpy.ops.group.create(name='MazeGeneratorDoNotTouch')


def choose_tile(maze, space_index):
    """Chooses what tile to add based on surrounding spaces in maze.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path], 
            [(space in maze - x, y), is path, is walkable, active path], ...]
        space_index - index of space to find tile for
    
    Returns:
        tile name, rotation tile should have
    """
    tile = ''
    rotation = 0

    # find out how many spaces that are touching are paths
    paths_found = 0
    touching, directions, _ = auto_layout_gen.find_touching(maze, space_index)
    for touching_space in touching:
        if maze[touching_space][1]:
            paths_found += 1

    # FLOOR PIECES!

    # start with floor pieces
    if maze[space_index][1]:
        if paths_found == 4:
            tile = 'floor_4_sided'
            return tile, rotation
        
        elif paths_found == 3:
            tile = 'floor_3_sided'

            # determine rotation (don't know if this translates directly)
            if directions == ['Up','Right','Down']:
                rotation = 90
            elif directions == ['Up','Right','Left']:
                rotation = 180
            elif directions == ['Up','Down','Left']:
                rotation = 270

            return tile, rotation
        
        elif paths_found == 1:
            tile = 'floor_1_sided'

            # determine rotation
            if directions == ['Right']:
                rotation = 90
            elif directions == ['Up']:
                rotation = 180
            elif directions == ['Left']:
                rotation = 270

            return tile, rotation

        elif paths_found == 0:
            tile = 'floor_0_sided'

            return tile, rotation

        # if 2 paths determine corner or straight
        elif paths_found == 2:

            # determine tile: first straight, then corner
            if directions == ['Up', 'Down'] or directions == ['Right', 'Left']:
                tile = 'floor_2_sided'

                # determine rotation
                if directions == ['Right', 'Left']:
                    rotation = 90

                return tile, rotation

            else:
                tile = 'floor_corner'

                # determine rotation
                if directions == ['Up', 'Right']:
                    rotation = 90
                elif directions == ['Up', 'Left']:
                    rotation = 180
                elif directions == ['Down', 'Left']:
                    rotation = 270
            
                return tile, rotation

    # WALL PIECES!

    # rule out pieces by number of paths_found (2 paths is in next block)
    if paths_found == 4:
        tile = 'wall_4_sided'
        return tile, rotation
    
    elif paths_found == 3:
        tile = 'wall_3_sided'

        # determine rotation
        if directions == ['Up','Right','Down']:
            rotation = 90
        elif directions == ['Up','Right','Left']:
            rotation = 180
        elif directions == ['Up','Down','Left']:
            rotation = 270

        return tile, rotation

    elif paths_found == 1:
        tile = 'wall_1_sided'

        # determine rotation
        if directions == ['Right']:
            rotation = 90
        elif directions == ['Up']:
            rotation = 180
        elif directions == ['Left']:
            rotation = 270

        return tile, rotation

    elif paths_found == 0:
        tile = 'wall_0_sided'

        return tile, rotation

    # if 2 paths determine corner or straight
    elif paths_found == 2:

        # determine tile: first straight, then corner
        if directions == ['Up', 'Down'] or directions == ['Right', 'Left']:
            tile = 'wall_2_sided'

            # determine rotation
            if directions == ['Right', 'Left']:
                rotation = 90

            return tile, rotation

        else:
            tile = 'wall_corner'

            # determine rotation
            if directions == ['Up', 'Right']:
                rotation = 90
            elif directions == ['Up', 'Left']:
                rotation = 180
            elif directions == ['Down', 'Left']:
                rotation = 270
        
            return tile, rotation


def make_tile_maze(maze):
    """Makes tile-based maze.
    
    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path], 
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    s_time = time()
    
    bpy.context.window_manager.progress_begin(1, 100)
    index = 0
    genloops = 0
    last_percent = None
    for space in maze:
        tile, rotation = choose_tile(maze, index)
        add_tile(tile, maze[index][0], rotation)

        genloops += 1
        
        percent = round((genloops/len(maze))*100)
        if percent != last_percent and percent < 100:
            bpy.context.window_manager.progress_update(percent)
            
            # new printout technique
            console_prog("Tile Maze Gen", genloops/len(maze))
            
            last_percent = percent
            
        index += 1

    # printout finished
    console_prog("Tile Maze Gen", 1, time() - s_time)
    print("\n")

    for active in bpy.context.selected_objects:
        bpy.context.scene.objects.active = active
        bpy.ops.object.select_grouped(type='GROUP')
        
    if bpy.context.scene.apply_modifiers:
        # apply modifiers
        for active in bpy.context.selected_objects:
            bpy.context.scene.objects.active = active
            mod_list = bpy.context.object.modifiers.values()
            for modifier in mod_list:
                name = modifier.name
                
                # this is messed up!!! because group is not created if merge 
                # objs is false! pseudo-fix at UI level by disabling option
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=name)
                
    else:
        for active in bpy.context.selected_objects:
            bpy.context.scene.objects.active = active
                
    if bpy.context.scene.merge_objects:
        bpy.ops.object.join()
        bpy.ops.group.objects_remove(group='MazeGeneratorDoNotTouch')

        # get 3D Cursor location
        cursor_x = bpy.context.space_data.cursor_location[0]
        cursor_y = bpy.context.space_data.cursor_location[1]
        cursor_z = bpy.context.space_data.cursor_location[2]
        
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # restore 3D cursor location
        bpy.context.space_data.cursor_location[0] = cursor_x
        bpy.context.space_data.cursor_location[1] = cursor_y
        bpy.context.space_data.cursor_location[2] = cursor_z
        
        bpy.context.object.name = "Maze"
        bpy.ops.object.transform_apply(location=False, rotation=True, 
            scale=False)

        # remove doubles
        if bpy.context.scene.remove_doubles_merge:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()

    bpy.context.window_manager.progress_end()