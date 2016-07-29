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
import sys
from time import time

import bpy

from random_probability import rand_prob

def console_prog(job, progress, total_time="?"):
    """Displays progress in the console.

    Args:
        job - name of the job
        progress - progress as a decimal number
        total_time (optional) - the total amt of time the job
                                took for final display
    """
    length = 20
    block = int(round(length * progress))
    message = "\r{0}: [{1}{2}] {3:.0%}".format(job, "#" * block, "-" * (length - block), progress)
    # progress is complete
    if progress >= 1:
        message = "\r{} DONE IN {} SECONDS{}".format(job.upper(), total_time, " " * 12)
    sys.stdout.write(message)
    sys.stdout.flush()


def exist_test((x,y)):
    """Check if ordered pair exists with maze size.

    Args:
        (x, y) - the ordered pair to check

    Returns:
        exists T/F, maze index of ordered pair
    """

    x_dimensions = bpy.context.scene.mg_width
    y_dimensions = bpy.context.scene.mg_height

    exists = False
    index = None

    # if x and y are greater than or equal to 0 - the left and top bounds &
    # if x and y are less than their respective dimensions - the right
    # and bottom bounds
    if x >= 0 and y >= 0 and x < x_dimensions and y < y_dimensions:
        exists = True

        # simple formula to determine index of ordered pair
        index = (x + (y * x_dimensions))

    return exists, index


def find_touching(maze, space, dist=1):
    """Find the spaces that touch the active space.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
        space - the start location of maze (currently top left corner)
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
    # find spaces touching space (an index)

    space_coord = maze[space][0]

    touching_xy = []
    directions = []
    all_directions = []

    new_touching_xy = (space_coord[0], space_coord[1] - dist)
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Up']
        if maze[index][1]:
            directions += ['Up']

    new_touching_xy = (space_coord[0] + dist, space_coord[1])
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Right']
        if maze[index][1]:
            directions += ['Right']

    new_touching_xy = (space_coord[0], space_coord[1] + dist)
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Down']
        if maze[index][1]:
            directions += ['Down']

    new_touching_xy = (space_coord[0] - dist, space_coord[1])
    exist, index = exist_test(new_touching_xy)
    if exist:
        touching_xy += [index]
        all_directions += ['Left']
        if maze[index][1]:
            directions += ['Left']

    # directions is the directions that is_path is True,
    # all_directions is all directions that exist
    return touching_xy, directions, all_directions


def valid_test(maze, existing_spaces, active_space, all_directions):
    """Get valid spaces based on rules.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
        existing_spaces - all spaces around active that are in the maze
        active_space - the current space
        all_directions - a list of directions that correspond to ex._sp.?

    Returns:
        list of valid spaces, list of valid directions
    """

    # existing_spaces is a list of indexes
    valid = []
    valid_dir = []
    count = 0
    for space in existing_spaces:
        # find spaces around an existing space
        touching_spaces, _, _ = find_touching(maze, space)

        # find paths around
        paths_found = 0
        for i in touching_spaces:
            if maze[i][1]:
                paths_found += 1

        # these are the rules
        # if I move there I must:
        # 1. Not be touching 2 paths
        # 2. Not be walking on an unwalkable space
        # 3. Not be walking on the active path (this may be removeable)
        if paths_found < 2 and maze[space][2] == True and maze[space][3] == False:

            if bpy.context.scene.allow_islands:
                valid += [space]
                valid_dir += all_directions[count]
            else:
                # if we don't allow islands we need to know if going
                # horizontal or vertical
                x_coord = maze[space][0][0]
                y_coord = maze[space][0][1]

                horizontal = False
                vertical = False

                # if we go right or left its horizontal, otherwise vertical
                if all_directions[count] == 'Right' or all_directions[count] == 'Left':
                    horizontal = True
                else:
                    vertical = True

                # if we are going horizontally on an even y value...we're good
                if y_coord % 2 == 0 and horizontal:
                    valid += [space]
                    valid_dir += all_directions[count]

                # if we are going vertically on an even x value...we're good
                if x_coord % 2 == 0 and vertical:
                    valid += [space]
                    valid_dir += all_directions[count]
        count += 1

    count = 0
    for space in existing_spaces:
        # find if space is an active_path
        active_path = False
        if maze[space][3]:
            active_path = True

        # if I run out of options (len(valid) is 0) and the space is an
        # active_path then it is added to valid list and the active_space
        # is set to not be walkable and active path = False
        if not valid and active_path:
            valid += [space]
            valid_dir += all_directions[count]
            maze[active_space][2] = False
            maze[active_space][3] = False
        count += 1

    return valid, all_directions


def make_path(maze, path_index):
    """Makes a maze[path_index] a path and makes it active.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
        path_index - index of maze to make a path

    Returns:
        updated maze
    """
    maze[path_index][1] = True
    maze[path_index][3] = True
    return maze


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


def check_completion(start_space, random_index):
    """Checks if maze generation is complete.

    Args:
        start_space - the start location of maze (currently top left corner)
        random_index - path choice
    """
    complete = False
    if random_index == start_space:
        complete = True
    return complete


def make_list_maze():
    """Constructs a python list maze based on maze gen settings.

    Returns:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    s_time = time()
    if not debug:
        print("\n")
    loops = 0

    bpy.context.window_manager.progress_begin(0, 100)

    x_dim = bpy.context.scene.mg_width
    y_dim = bpy.context.scene.mg_height
    estimated_loops = int((x_dim * y_dim * 1.25))

    # generate blank grid (list) False everywhere (walls)
    maze = []
    for y in range(0, y_dim):
        for x in range(0, x_dim):
            # [[space in maze(ordered pair),is path,is walkable,active path]]
            maze_addition = [[(x, y), False, True, False]]
            maze += maze_addition

    # start at a point and generate maze's path
    start_space = 0
    complete = False
    maze = make_path(maze, start_space)
    random_index = start_space

    # initialize to none instead of 0 so that it will print 0 b/c 0 != last_percent = None
    last_percent = None

    while not complete:
        loops += 1
        existing_spaces, _, all_directions = find_touching(
            maze, random_index)

        valid, all_directions = valid_test(
            maze, existing_spaces, random_index, all_directions)

        random_index = random.choice(valid)

        maze = make_path(maze, random_index)

        complete = check_completion(start_space, random_index)

        # update printout
        percent = int((loops / estimated_loops) * 100)
        if percent != last_percent and percent < 100:
            bpy.context.window_manager.progress_update(percent)
            if not debug:
                console_prog("Layout Gen", loops / estimated_loops)
        last_percent = percent
        
    # print out finished job
    if not debug:
        console_prog("Layout Gen", 1, time() - s_time)
        print("\n")
    bpy.context.window_manager.progress_end()

    return maze
