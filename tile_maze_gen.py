"""
Tile-based maze generation.

Available Functions:
    console_prog - Displays progress in the console
    add_tile - Adds a tile object to the scene at certain transform
    choose_tile - Chooses what tile to add based on surrounding spaces in maze
    make_tile_maze - Makes tile-based maze
"""

import math

import bpy
from maze_gen.progress_display import BlenderProgress


def add_tile(tile, x_location, y_location, rotation):
    """Adds a tile object to the scene at certain transform.

    Args:
        tile - tile to add
        location - location component of desired transform
        rotation - rotation component of desired transform
    """

    # setup tiles for reference
    # 12 tile gen
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

    # 6 tile gen
    four_way = bpy.context.scene.four_way
    t_int = bpy.context.scene.t_int
    turn = bpy.context.scene.turn
    dead_end = bpy.context.scene.dead_end
    straight = bpy.context.scene.straight
    no_path = bpy.context.scene.no_path

    # clear selection
    bpy.ops.object.select_all(action='DESELECT')

    # select object correct tile
    # 12 tile gen
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
    # 6 tile gen
    elif tile == 'four_way':
        bpy.data.objects[four_way].select = True
    elif tile == 't_int':
        bpy.data.objects[t_int].select = True
    elif tile == 'turn':
        bpy.data.objects[turn].select = True
    elif tile == 'dead_end':
        bpy.data.objects[dead_end].select = True
    elif tile == 'straight':
        bpy.data.objects[straight].select = True
    elif tile == 'no_path':
        bpy.data.objects[no_path].select = True

    # ensure there is an active object
    bpy.context.scene.objects.active = bpy.context.selected_objects[0]

    # select children
    bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

    # duplicate and move
    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
        TRANSFORM_OT_translate={"value": (0, 0, 0),
                                "constraint_axis": (False, False, False),
                                "constraint_orientation": 'GLOBAL',
                                "mirror": False,
                                "proportional": 'DISABLED',
                                "proportional_edit_falloff": 'SMOOTH',
                                "proportional_size": 1,
                                "snap": False,
                                "snap_target": 'CLOSEST',
                                "snap_point": (0, 0, 0),
                                "snap_align": False,
                                "snap_normal": (0, 0, 0),
                                "gpencil_strokes": False,
                                "texture_space": False,
                                "remove_on_cancel": False,
                                "release_confirm": False})

    tile_parent = bpy.context.scene.objects.active

    tile_parent.location[0] = x_location
    tile_parent.location[1] = -y_location
    tile_parent.rotation_euler[2] = math.radians(rotation)

    if bpy.context.scene.merge_objects:
        # add to group MazeGeneratorDoNotTouch
        for active in bpy.context.selected_objects:
            bpy.context.scene.objects.active = active
            try:
                bpy.ops.object.group_link(group='MazeGeneratorDoNotTouch')
            except TypeError:
                bpy.ops.group.create(name='MazeGeneratorDoNotTouch')


def choose_tile(maze, x, y):
    """Chooses what tile to add based on surrounding spaces in maze.

    Returns:
        tile name, rotation tile should have
    """

    # find out how many spaces that are touching are paths
    directions = maze.find_touching_path_dirs(x, y)

    tm = bpy.context.scene.tile_mode

    if tm == "TWELVE_TILES":
        floor_possibilities = {
            # four-way floor
            ('N', 'W', 'E', 'S'): ('floor_4_sided', 0),
            # three-way floor
            ('W', 'E', 'S'): ('floor_3_sided', 180),
            ('N', 'E', 'S'): ('floor_3_sided', 90),
            ('N', 'W', 'E'): ('floor_3_sided', 0),
            ('N', 'W', 'S'): ('floor_3_sided', 270),
            # dead-end floor
            ('S',): ('floor_1_sided', 180),
            ('E',): ('floor_1_sided', 90),
            ('N',): ('floor_1_sided', 0),
            ('W',): ('floor_1_sided', 270),
            # solitary floor
            (): ('floor_0_sided', 0),
            # straight path floor
            ('N', 'S'): ('floor_2_sided', 0),
            ('W', 'E'): ('floor_2_sided', 90),
            # turn floor
            ('E', 'S'): ('floor_corner', 90),
            ('N', 'E'): ('floor_corner', 0),
            ('N', 'W'): ('floor_corner', 270),
            ('W', 'S'): ('floor_corner', 180),
        }

        wall_possibilities = {
            # solitary wall
            ('N', 'W', 'E', 'S'): ('wall_4_sided', 0),
            # end of wall
            ('W', 'E', 'S'): ('wall_3_sided', 180),
            ('N', 'E', 'S'): ('wall_3_sided', 90),
            ('N', 'W', 'E'): ('wall_3_sided', 0),
            ('N', 'W', 'S'): ('wall_3_sided', 270),
            # side of wall block
            ('S',): ('wall_1_sided', 180),
            ('E',): ('wall_1_sided', 90),
            ('N',): ('wall_1_sided', 0),
            ('W',): ('wall_1_sided', 270),
            # center of wall block
            (): ('wall_0_sided', 0),
            # straight wall between two paths
            ('N', 'S'): ('wall_2_sided', 0),
            ('W', 'E'): ('wall_2_sided', 90),
            # corner wall
            ('E', 'S'): ('wall_corner', 90),
            ('N', 'E'): ('wall_corner', 0),
            ('N', 'W'): ('wall_corner', 270),
            ('W', 'S'): ('wall_corner', 180),
        }

        if maze.is_path(x, y):
            return floor_possibilities[tuple(directions)]
        else:
            return wall_possibilities[tuple(directions)]

    elif tm == 'SIX_TILES':
        possibilities = {
            # four-way floor
            ('N', 'W', 'E', 'S'): ('four_way', 0),
            # three-way floor
            ('W', 'E', 'S'): ('t_int', 180),
            ('N', 'E', 'S'): ('t_int', 90),
            ('N', 'W', 'E'): ('t_int', 0),
            ('N', 'W', 'S'): ('t_int', 270),
            # dead-end floor
            ('S',): ('dead_end', 180),
            ('E',): ('dead_end', 90),
            ('N',): ('dead_end', 0),
            ('W',): ('dead_end', 270),
            # solitary wall
            (): ('no_path', 0),
            # straight path floor
            ('N', 'S'): ('straight', 0),
            ('W', 'E'): ('straight', 90),
            # turn floor
            ('E', 'S'): ('turn', 90),
            ('N', 'E'): ('turn', 0),
            ('N', 'W'): ('turn', 270),
            ('W', 'S'): ('turn', 180),
        }

        # to add in six tile mode the space must be a path and it's x and y must both be even
        if maze.is_path(x, y) and not x & 1 and not y & 1:
            return possibilities[tuple(directions)]
        else:
            return "", 0  # empty tile to show not to add anything


def make_tile_maze(maze):
    """Makes tile-based maze.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    bldr_prog = BlenderProgress("Tile Maze Gen", debug)
    genloops = 0
    for row in range(maze.width):
        for column in range(maze.height):
            # choose tile
            tile, rotation = choose_tile(maze, row, column)
            if tile:
                add_tile(tile, row, column, rotation)

            genloops += 1
            progress = genloops / len(maze)
            bldr_prog.update(progress)

    # make sure there is an active object
    bpy.context.scene.objects.active = bpy.context.selected_objects[0]
    # select all objects in that group
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

    bldr_prog.finish()
