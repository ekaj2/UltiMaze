"""
Generates maze layout.

Available Functions:
    console_prog - Displays progress in the console
    exist_test - Check if ordered pair exists with maze size
    find_touching - Find the spaces that touch the active space
    valid_test - Get valid spaces based on rules
    choose_index - Randomly makes a choice out of possibilities
    make_path - Makes a maze[path_index] a path and makes it active
    add_loops - Adds the ability to walk in circles by removing walls
    check_completion - Checks if maze generation is complete
    make_list_maze - Constructs a python list maze based on maze gen settings
"""

import random

import bpy
from maze_gen import maze_tools


# here for compatibility with other modules
def find_touching(maze, active_space, dist=1):
    """
    OUTDATED!!! ONLY HERE UNTIL ALL REFERENCES HAVE BEEN CHANGED!!!

    Find the spaces that touch the active space.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
        active_space - the start location of maze (currently top left corner)
        dist - distance from start space

            ---------------------
            |   |   | 2 |   |   |
            ---------------------
            |   |   | 1 |   |   |
            ---------------------
            | 2 | 1 | # | 1 | 2 |
            ---------------------
            |   |   | 1 |   |   |
            ---------------------
            |   |   | 2 |   |   |
            ---------------------

    Returns:
        indexes of touching spaces, directions that is_path is True,
        all directions that exist
    """
    # find spaces touching active_space (an index)

    active_space_coord = maze[active_space][0]

    touching_xy = []
    directions = []
    all_directions = []

    new_touching_xy = [((active_space_coord[0]), (active_space_coord[1] - dist))]
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Up']
        if maze[index][1]:
            directions += ['Up']

    new_touching_xy = [((active_space_coord[0] + dist), (active_space_coord[1]))]
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Right']
        if maze[index][1]:
            directions += ['Right']

    new_touching_xy = [((active_space_coord[0]), (active_space_coord[1] + dist))]
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Down']
        if maze[index][1]:
            directions += ['Down']

    new_touching_xy = [((active_space_coord[0] - dist), (active_space_coord[1]))]
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Left']
        if maze[index][1]:
            directions += ['Left']

    # directions is the directions that is_path is True,
    # all_directions is all directions that exist
    return touching_xy, directions, all_directions


def exist_test(ordered_pair):
    """
    OUTDATED!!! ONLY HERE UNTIL ALL REFERENCES HAVE BEEN CHANGED!!!

    Check if ordered pair exists with maze size.

    Args:
        ordered_pair - the ordered pair to check

    Returns:
        exists T/F, maze index of ordered pair
    """

    x_dimensions = bpy.context.scene.mg_width
    y_dimensions = bpy.context.scene.mg_height

    exists = False
    index = None

    x = ordered_pair[0][0]
    y = ordered_pair[0][1]

    # if x and y are greater than or equal to 0 - the left and top bounds &
    # if x and y are less than their respective dimensions - the right
    # and bottom bounds
    if x >= 0 and y >= 0 and x < x_dimensions and y < y_dimensions:
        exists = True

        # simple formula to determine index of ordered pair
        index = (x + (y * x_dimensions))

    return exists, index


def add_loops(maze):
    """Adds the ability to walk in circles by removing walls.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]

    Returns:
        updated maze
    """
    chance = bpy.context.scene.loops_chance
    for i, space in enumerate(maze):
        _, directions, _ = find_touching(maze, i)
        if directions == ['Up', 'Down'] or directions == ['Right', 'Left']:
            random_num = random.randint(1, chance)
            if random_num == 1:
                maze[i][1] = True

    return maze


def make_list_maze():
    """Constructs a python list maze based on maze gen settings.

    Returns:
        maze - python list in the format:
            [[(space in maze - x, y), is path],
            [(space in maze - x, y), is path], ...]
    """
    scene = bpy.context.scene
    x_dim = scene.mg_width
    y_dim = scene.mg_height
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    if scene.algorithm == 'BREADTH_FIRST':
        m = maze_tools.BreadthFirstGridMaze(debug, x_dim, y_dim)
    elif scene.algorithm == 'DEPTH_FIRST':
        m = maze_tools.DepthFirstGridMaze(debug, x_dim, y_dim)
    elif scene.algorithm == 'PRIMS':
        m = maze_tools.PrimsGridMaze(debug, x_dim, y_dim)
    elif scene.algorithm == 'BINARY_TREE':
        m = maze_tools.BinaryTreeGridMaze(debug, x_dim, y_dim)  # TODO - add ui directions

    maze = m.get()
    
    # a bit of a hack for now to avoid changing the maze format everywhere just yet...converts to old style
    old_maze = []
    for y in range(0, y_dim):
        for x in range(0, x_dim):
            # [[space in maze(ordered pair),is path]]
            old_maze += [[(x, y), maze[x][y]]]

    return old_maze
