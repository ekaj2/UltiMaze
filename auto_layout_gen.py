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
IN_BLENDER = False

import random
import sys
from time import time, sleep

if IN_BLENDER:
    import bpy

from random_probability import rand_prob


def find_touching(self, space, dist=1):
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
    offsets = [(0, -dist), (dist, 0), (0, dist), (-dist, 0)]
    
    touching_xy = []
    for offset in offsets:
        new_touching_xy = (self.maze[space][0][0] + offset[0], self.maze[space][0][1] + offset[1])
        exist, index = self.exist_test(new_touching_xy)
        if exist:
            touching_xy += [index]
    return touching_xy

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


class Maze(object):
    global IN_BLENDER
    
    maze = []
    cells = []
    show = False
        
    if IN_BLENDER:
        debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode
    else:
        debug = True
        
    def __init__(self, x_dim=10, y_dim=10):
        self.x_dim = x_dim
        self.y_dim = y_dim
        
        # generate blank grid (list) False everywhere (walls)
        # maze = [[0:x_dim][0:y_dim]]
        # 3x3 maze
        # maze = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        for column in range(0, self.x_dim):
            self.maze += [[]]
            for row in range(0, self.y_dim):
                self.maze[column] += [0]
        self.display()
    
    def make(self, show=False):
        global IN_BLENDER
        
        self.show = show
        
        estimated_loops = int((self.x_dim * self.y_dim * 1.25))
        
        # select a cell and add it to the cells list - this could be random
        #self.cells += [(random.randint(0, self.x_dim - 1), random.randint(0, self.y_dim - 1))]
        x, y = 0, 0
        self.cells += [(x, y)]
        self.maze[x][y] = 1
    
        # initialize to none instead of 0 so that it will print 0 b/c 0 != last_percent = None
        last_percent = None
        loops = 0
        while self.cells:
            
            # choose index from cells list
            index = self.choose_ind()
            sleep(0.5)
            print("index:", index, ", cells:", self.cells)
            
            # get ordered pair of selected cell
            x, y = self.cells[index][0], self.cells[index][1]
            
            # shuffle cardinal directions
            directions = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]

            random.shuffle(directions)
            
            for dir in directions:
                dx, dy = dir
                print("dir:", dir, ", exists:", self.exist_test(dir)[0])
                
                go_ahead = True
                
                # check that we're on evens
                if dx % 2 or dy % 2:
                    go_ahead = False
                
                # check that we're not by a path cell
                directions2 = [(dx, dy + 1), (dx + 1, dy), (dx, dy - 1), (dx - 1, dy)]
                found_paths = 0
                for d in directions2:
                    if self.maze[d[0]][d[1]]:
                        found_paths += 1
                
                if self.exist_test(dir)[0] and self.maze[dir[0]][dir[1]] == 0 and go_ahead:
                    print(self.maze[dx][dy])
                    self.maze[dx][dy] = 1
                    self.cells += [(dx, dy)]
                    index = None
                    break
                
            # remove from cells list if index has not been found
            if index != None:
                self.cells.pop(index)
            
            self.display()
                                            
            # update printout
            loops += 1
            percent = int((loops / estimated_loops) * 100)
            if percent != last_percent and percent < 100:
                if IN_BLENDER:
                    bpy.context.window_manager.progress_update(percent)
                    if not self.debug:
                        console_prog("Layout Gen", loops / estimated_loops)
            last_percent = percent
    
    def choose_ind(self):
        return len(self.cells) - 1
    
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
        if x >= 0 and y >= 0 and x < self.x_dim and y < self.y_dim:
            exists = True
    
            # determine index of ordered pair
            index = (x + (y * self.x_dim))
    
        return exists, index


    def find_touching(self, space, dist=1):
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
        offsets = [(0, -dist), (dist, 0), (0, dist), (-dist, 0)]
        
        touching_xy = []
        for offset in offsets:
            new_touching_xy = (self.maze[space][0][0] + offset[0], self.maze[space][0][1] + offset[1])
            exist, index = self.exist_test(new_touching_xy)
            if exist:
                touching_xy += [index]
        return touching_xy
    
    def get(self):
        return self.maze
    
    def display(self):
        disp = ""
        for row in range(self.y_dim):
            for column in range(self.x_dim):
                if self.maze[column][row]:
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
        
    m = Maze(x_dim, y_dim)
    m.make()
    maze = m.get()
    
        
    # print out finished job
    if not debug:
        console_prog("Layout Gen", 1, time() - s_time)
        print("\n")
    bpy.context.window_manager.progress_end()

    return maze


def main():
    m = Maze()
    m.make(show=True)
#     maze = m.get()

if __name__ == "__main__":
    main() 