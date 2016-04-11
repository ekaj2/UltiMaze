import math
import random
import sys
from time import time

import bpy

def console_prog(job, progress, total_time="?"):
    length = 20
    block = int(round(length*progress))
    message = "\r{0}: [{1}{2}] {3:.0%}".format(job, "#"*block, "-"*(length-block), progress)
    # progress is complete
    if progress >= 1:
        message = "\r{} DONE IN {} SECONDS{}".format(job.upper(), total_time, " "*12)
    sys.stdout.write(message)
    sys.stdout.flush()


def exist_test(grid, ordered_pair):

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
        index = (x + (y * (x_dimensions)))

    return exists, index


def find_touching(maze,start_space):
    # find spaces touching start_space (an index)
    
    start_space_coord = maze[start_space][0]

    touching_XY = []
    directions = []
    all_directions = []

    new_touching_XY = [((start_space_coord[0]),(start_space_coord[1]-1))]
    exist, index = exist_test(maze, new_touching_XY)
    if exist:
        touching_XY += [index]
        all_directions += ['Up']
        if maze[index][1]:
            directions += ['Up']

    new_touching_XY = [((start_space_coord[0]+1),(start_space_coord[1]))]
    exist, index = exist_test(maze, new_touching_XY)
    if exist:
        touching_XY += [index]
        all_directions += ['Right']
        if maze[index][1]:
            directions += ['Right']

    new_touching_XY = [((start_space_coord[0]),(start_space_coord[1]+1))]
    exist, index = exist_test(maze, new_touching_XY)
    if exist:
        touching_XY += [index]
        all_directions += ['Down']
        if maze[index][1]:
            directions += ['Down']

    new_touching_XY = [((start_space_coord[0]-1),(start_space_coord[1]))]
    exist, index = exist_test(maze, new_touching_XY)
    if exist:
        touching_XY += [index]
        all_directions += ['Left']
        if maze[index][1]:
            directions += ['Left']

    # directions is the directions that is_path is True, 
    # all_directions is all directions that exist
    return touching_XY, directions, all_directions


def valid_test(maze,existing_spaces,start_space, all_directions):
    # existing_spaces is a list of indexes
    
    valid = []
    valid_dir = []
    count = 0
    for space in existing_spaces:
        # find spaces around an existing space
        touching_spaces, _, _ = find_touching(maze,space)

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
        if (paths_found < 2 and maze[space][2] == True and 
            maze[space][3] == False):
                
            if bpy.context.scene.allow_islands:
                valid += [space]
                valid_dir += all_directions[count]
            else:
                # if we don't allow islands we need to know if going 
                # horizontal or vertical
                X_coord = maze[space][0][0]
                Y_coord = maze[space][0][1]
                
                horizontal = False
                vertical = False
                
                # if we go right or left its horizontal, otherwise vertical
                if (all_directions[count] == 'Right' or 
                    all_directions[count] == 'Left'):
                        
                    horizontal = True
                else:
                    vertical = True

                # if we are going horizontally on an even y value...we're good
                if Y_coord % 2 == 0 and horizontal:
                    valid += [space]
                    valid_dir += all_directions[count]
                    
                # if we are going vertically on an even x value...we're good
                if X_coord % 2 == 0 and vertical:
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
        # active_path then it is added to valid list and the start_space 
        # is set to not be walkable and active path = False
        if len(valid) == 0 and active_path:
            valid += [space]
            valid_dir += all_directions[count]
            maze[start_space][2] = False
            maze[start_space][3] = False

        count += 1
    return valid, all_directions
    

def choose_index(maze,choices):
    # choices is a list of indexes
    if len(choices) > 0:
        random_integer = random.randint(0,(len(choices)-1))
        random_index = choices[random_integer]
        return random_index, random_integer
    else:
        # this should never happen: only here for debugging
        print("No choices possible! We are gonna have some issues!")


def make_path(maze,path_index):
    maze[path_index][1] = True
    maze[path_index][3] = True
    return maze


def remove_paths(maze,wall_indexes):
    for space in wall_indexes:
        maze[space][1] = False
    return maze


def add_loops(maze):
    index = 0
    chance = bpy.context.scene.loops_chance
    for i, space in enumerate(maze):
        _, directions, _ = find_touching(maze, index)
        if directions == ['Up', 'Down'] or directions == ['Right', 'Left']:
            random_num = random.randint(1,chance)
            if random_num == 1:
                maze[i][1] = True

    return maze


def check_completion2(maze,start_space,random_index):
    complete = False
    if random_index == start_space:
        complete = True
    return complete


def make_list_maze():
    s_time = time()
    print("\n")
    loops = 0
    
    bpy.context.window_manager.progress_begin(0, 100)
        
    X_dim = bpy.context.scene.mg_width
    Y_dim = bpy.context.scene.mg_height
    estimated_loops = int((X_dim*Y_dim*1.25))
    
    # generate blank grid (list) False everywhere (walls)
    maze = []
    for y in range(0,Y_dim):
        for x in range(0,X_dim):
            # [[space in maze(ordered pair),is path,is walkable,active path]]
            maze_addition = [[(x,y),False,True,False]]
            maze += maze_addition

    # start at a point and generate maze's path
    start_space = 0
    complete = False
    maze = make_path(maze,start_space)
    random_index = start_space

    last_percent = None

    while not complete:
        loops += 1
        existing_spaces, directions, all_directions = find_touching(
            maze, random_index)
            
        valid, all_directions = valid_test(
            maze, existing_spaces, random_index, all_directions)
            
        random_index, choices_index = choose_index(maze, valid)
        
        maze = make_path(maze, random_index)
        
        complete = check_completion2(maze,start_space,random_index)
        
        percent = int((loops/estimated_loops)*100)
        if percent != last_percent and percent < 100:
            bpy.context.window_manager.progress_update(percent)
            
            # new print out technique
            console_prog("Layout Gen", loops / estimated_loops)

        last_percent = percent

    # print out finished job
    console_prog("Layout Gen", 1, time() - s_time)
    print("\n")
    bpy.context.window_manager.progress_end()

    return maze