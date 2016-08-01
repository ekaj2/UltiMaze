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
IN_BLENDER = True

import random
import sys
from time import time, sleep

if IN_BLENDER:
    import bpy

if IN_BLENDER:
    from maze_gen.random_probability import rand_prob
else:
    from random_probability import rand_prob


# here for compatibility with other modules
def find_touching(maze, active_space, dist=1):
    """Find the spaces that touch the active space.

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
    """Check if ordered pair exists with maze size.

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


def remove_doubles_list(a):
    """Removes list doubles in list where list(set(a)) will raise a TypeError."""
    clean_list = []
    for b in a:
        if b not in clean_list:
            clean_list += [b]
    return clean_list


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


class Maze():
    global IN_BLENDER
        
    def __init__(self, debug, x_dim=10, y_dim=10):
        
        self.debug = debug
        self.x_dim = x_dim
        self.y_dim = y_dim
        
        self.maze = []
        self.cells = []
        
        # generate blank grid (list) False everywhere (walls)
        # maze = [[0:x_dim][0:y_dim]]
        # 3x3 maze
        # maze = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        for column in range(0, self.x_dim):
            self.maze += [[]]
            for row in range(0, self.y_dim):
                self.maze[column] += [0]
        
        if self.debug:
            self.display()
    
    def make(self, algorithm1, algorithm2, mix):
        global IN_BLENDER
                
        estimated_loops = int((self.x_dim * self.y_dim * 1.25))
        
        # select a cell and add it to the cells list - this could be random
        x, y = random.randint(0, self.x_dim - 1), random.randint(0, self.y_dim - 1)
        self.cells += [(x, y)]
        self.maze[x][y] = 1
    
        # initialize to none instead of 0 so that it will print 0 b/c 0 != last_percent = None
        last_percent = None
        loops = 0
        while self.cells:
            
            # choose index from cells list
            index = self.choose_ind(rand_prob([[algorithm1, 100 - mix * 100], [algorithm2, mix * 100]]))
            
            # get ordered pair of selected cell
            x, y = self.cells[index][0], self.cells[index][1]
            
            # shuffle cardinal directions
            directions = [(x, y + 2), (x + 2, y), (x, y - 2), (x - 2, y)]

            random.shuffle(directions)
            
            illum_list = []
            
            for dir in directions:
                illum_list += [dir]
            
            for dir in directions:
                dx, dy = dir
                
                # check that we're not by more than 1 path cell
                if len(self.paths_only(self.find_touching((dx,dy)))) > 1:
                    continue
                
                if self.exist_test(dir)[0] and self.maze[dir[0]][dir[1]] == 0:
                    # space in between b/c we are doing doubles
                    print((x+dx)/2, (y+dy)/2)
                    self.maze[round((x+dx)/2)][round((y+dy)/2)] = 1
                    # space (second one)
                    self.maze[dx][dy] = 1
                    self.cells += [(dx, dy)]
                    index = None
                    break
                
            # remove from cells list if index has not been found
            if index is not None:
                self.cells.pop(index)
            
            if self.debug:
                print("\n\n\n\n\n")
                self.display(illum_list)

            # update printout
            loops += 1
            percent = int((loops / estimated_loops) * 100)
            if percent != last_percent and percent < 100:
                if IN_BLENDER:
                    bpy.context.window_manager.progress_update(percent)
                    if not self.debug:
                        console_prog("Layout Gen", loops / estimated_loops)
            last_percent = percent
          
        if self.debug:
            print("\n\n\n\n\n")
            self.display()
    
    def choose_ind(self, algorithm):
        if algorithm == 'DEPTH_FIRST':
            return len(self.cells) - 1
        elif algorithm == 'BREADTH_FIRST':
            return 0
        elif algorithm == 'PRIMS':
            return random.randint(0, len(self.cells) - 1)
    
    def exist_test(self, xy):
        """Check if ordered pair exists with maze size.
    
        Args:
            (x, y) - the ordered pair to check
    
        Returns:
            exists T/F, maze index of ordered pair
        """
        x, y = xy
        exists = False
        index = None
    
        # if x and y are greater than or equal to 0 - the left and top bounds &
        # if x and y are less than their respective dimensions - the right
        # and bottom bounds
        if self.x_dim > x >= 0 and self.y_dim > y >= 0:
            exists = True
    
            # determine index of ordered pair
            index = (x + (y * self.x_dim))
            if self.debug:
                print(x,y)
            
        return exists, index

    def find_touching(self, space, dist=1, diagonals=False):
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
            indexes of touching spaces
        """
        x, y = space
        if diagonals:
            directions = [(x - dist, y - dist), (x + dist, y + dist), (x + dist, y + dist), (x - dist, y - dist)]
        else:
            directions = [(x, y - dist), (x + dist, y), (x, y + dist), (x - dist, y)]
        
        touching_xy = []
        for dir in directions:
            if self.exist_test(dir)[0]:
                touching_xy += [dir]
            
        return touching_xy
    
    def paths_only(self, spaces):
        path_spaces = []
        for space in spaces:
            x,y = space
            if self.debug:
                print("paths_only:", x,y)
            if self.maze[x][y]:
                path_spaces += [space]
        return path_spaces
    
    def get(self):
        return self.maze
    
    def display(self, illum_list=()):
        disp = ""
        for y in range(self.y_dim):
            for x in range(self.x_dim):
                if (x, y) in illum_list:
                    disp += "$"
                elif self.maze[x][y]:
                    disp += " "
                else:
                    disp += "#"
            disp += "\n"
        print(disp)


def make_list_maze():
    """Constructs a python list maze based on maze gen settings.

    Returns:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    scene = bpy.context.scene
    x_dim = scene.mg_width
    y_dim = scene.mg_height
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    # display setups
    bpy.context.window_manager.progress_begin(0, 100)
    s_time = time()
    if not debug:
        print("\n")
        
    m = Maze(debug, x_dim, y_dim)
    m.make(scene.algorithm1, scene.algorithm2, scene.algorithm_mix)
    maze = m.get()
    
    # a bit of a hack for now to avoid changing the maze format everywhere just yet...converts to old style
    old_maze = []
    for y in range(0, y_dim):
        for x in range(0, x_dim):
            # [[space in maze(ordered pair),is path]]
            old_maze += [[(x, y), maze[x][y]]]
        
    # print out finished job
    if not debug:
        console_prog("Layout Gen", 1, time() - s_time)
        print("\n")
    bpy.context.window_manager.progress_end()

    return old_maze


def main():
    m = Maze(9,9)
    m.make('PRIMS')
#     maze = m.get()

if __name__ == "__main__":
    main() 