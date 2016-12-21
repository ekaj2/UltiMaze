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
    objects = bpy.context.scene.objects

    # 12 tile gen
    if tile == 'wall_4_sided':
        copy = objects['wall_4_sided'].copy()
    elif tile == 'wall_3_sided':
        copy = objects['wall_3_sided'].copy()
    elif tile == 'wall_2_sided':
        copy = objects['wall_2_sided'].copy()
    elif tile == 'wall_1_sided':
        copy = objects['wall_1_sided'].copy()
    elif tile == 'wall_0_sided':
        copy = objects['wall_0_sided'].copy()
    elif tile == 'wall_corner':
        copy = objects['wall_corner'].copy()
    elif tile == 'floor_4_sided':
        copy = objects['floor_4_sided'].copy()
    elif tile == 'floor_3_sided':
        copy = objects['floor_3_sided'].copy()
    elif tile == 'floor_2_sided':
        copy = objects['floor_2_sided'].copy()
    elif tile == 'floor_1_sided':
        copy = objects['floor_1_sided'].copy()
    elif tile == 'floor_0_sided':
        copy = objects['floor_0_sided'].copy()
    elif tile == 'floor_corner':
        copy = objects['floor_corner'].copy()
    # 6 tile gen
    elif tile == 'four_way':
        copy = objects['four_way'].copy()
    elif tile == 't_int':
        copy = objects['t_int'].copy()
    elif tile == 'turn':
        copy = objects['turn'].copy()
    elif tile == 'dead_end':
        copy = objects['dead_end'].copy()
    elif tile == 'straight':
        copy = objects['straight'].copy()
    elif tile == 'no_path':
        copy = objects['no_path'].copy()

    # duplicate and move
    scene = bpy.context.scene
    copy.data = copy.data.copy()
    scene.objects.link(copy)
    copy['MazeGeneratorDoNotTouch'] = True
    scene.objects.active = copy

    copy.location[0] = x_location
    copy.location[1] = -y_location
    copy.rotation_euler[2] = math.radians(rotation)


def choose_tile(maze, x, y):
    """Chooses what tile to add based on surrounding spaces in maze.

    Returns:
        tile name, rotation tile should have
    """
    # find out how many spaces that are touching are paths
    directions = maze.find_touching_path_dirs(x, y)

    tm = bpy.context.scene.mg.tile_mode

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

        if maze.exist_test(x, y) and maze.is_path(x, y):
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
        if maze.exist_test(x, y) and maze.is_path(x, y) and not x & 1 and not y & 1:
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
    scene = bpy.context.scene
    mg = scene.mg
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    bpy.ops.object.select_all(action='DESELECT')

    bldr_prog = BlenderProgress("Tile Maze Gen", debug)
    bldr_prog.start()
    genloops = 0
    for row in range(maze.height):
        for column in range(maze.width):
            tile, rotation = choose_tile(maze, column, row)
            if tile:
                add_tile(tile, column, row, rotation)

            genloops += 1
            progress = genloops / (maze.width * maze.height)
            bldr_prog.update(progress)
    scene.update()
    bldr_prog.finish()

    for obj in scene.objects:
        if obj.get("MazeGeneratorDoNotTouch"):
            obj.select = True

    if mg.apply_modifiers:
        for obj in bpy.context.selected_objects:
            scene.objects.active = obj
            mod_list = obj.modifiers.values()
            for modifier in mod_list:
                name = modifier.name
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=name)
    else:
        scene.objects.active = bpy.context.object

    if mg.merge_objects:
        bpy.ops.object.join()

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
        if mg.remove_doubles_merge:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
    else:
        bpy.ops.object.select_all(action='DESELECT')

    for obj in scene.objects:
        if obj.get("MazeGeneratorDoNotTouch"):
            del obj['MazeGeneratorDoNotTouch']

