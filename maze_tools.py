IN_BLENDER = False

import random

if IN_BLENDER:
    from maze_gen.random_probability import rand_prob
    from maze_gen.progress_display import BlenderProgress
else:
    from random_probability import rand_prob
    from time import sleep


class Maze:
    """Flexible and powerful maze generation class.

    Methods:
        __init__ - Creates maze grid and initializes variables.
        make - Makes a maze.
        choose_ind -  Chooses index based on algorithm parameter.
        exist_test - Checks if ordered pair exists within maze size.
        find_touching - Finds the spaces that touch 'space' separated by 'dist'.
        paths_only - Filters out all wall spaces from a list of spaces.
        get - Returns maze.
        display - Prints maze to terminal or console window.
    """

    global IN_BLENDER

    def __init__(self, debug, x_dim=10, y_dim=10):
        """Creates maze grid and initializes variables."""

        self.debug = debug
        self.x_dim = x_dim
        self.y_dim = y_dim

        self.maze = []
        self.cells = []

        for column in range(0, self.x_dim):
            self.maze += [[]]
            for row in range(0, self.y_dim):
                self.maze[column] += [0]

    def make(self, algorithm1, algorithm2, mix):
        """Makes a maze.

        Args:
            algorithm1 - first algorithm to mix
            algorithm2 - second algorithm to mix
            mix - factor to mix algorithms with
        """
        global IN_BLENDER

        estimated_loops = int((self.x_dim * self.y_dim * 1.25))

        if IN_BLENDER:
            bldr_prog = BlenderProgress("Layout Gen", self.debug)
            bldr_prog.start()

        # select a cell and add it to the cells list - this could be random
        x, y = random.randint(0, self.x_dim - 1), random.randint(0, self.y_dim - 1)
        self.cells += [(x, y)]
        self.maze[x][y] = 1

        loops = 0
        while self.cells:

            # choose index from cells list
            index = self.choose_ind(rand_prob([[algorithm1, 100 - mix * 100], [algorithm2, mix * 100]]))

            # get ordered pair of selected cell
            x, y = self.cells[index][0], self.cells[index][1]

            # shuffle cardinal directions
            directions = [(x, y + 2), (x + 2, y), (x, y - 2), (x - 2, y)]

            random.shuffle(directions)

            for dir in directions:
                dx, dy = dir

                # check that we're not by more than 1 path cell
                if len(self.paths_only(self.find_touching((dx, dy)))) > 1:
                    continue

                if self.exist_test(dir) and self.maze[dir[0]][dir[1]] == 0:
                    # space in between b/c we are doing doubles
                    self.maze[round((x + dx) / 2)][round((y + dy) / 2)] = 1
                    # space (second one)
                    self.maze[dx][dy] = 1
                    self.cells += [(dx, dy)]
                    index = None
                    break

            # remove from cells list if index has not been found
            if index is not None:
                self.cells.pop(index)

            loops += 1

            if IN_BLENDER:
                progress = loops / estimated_loops
                bldr_prog.update(progress)

            else:
                self.display()
                sleep(0.5)

        if IN_BLENDER:
            bldr_prog.finish()

    def choose_ind(self, algorithm):
        """Chooses index based on algorithm parameter."""

        if algorithm == 'DEPTH_FIRST':
            return len(self.cells) - 1
        elif algorithm == 'BREADTH_FIRST':
            return 0
        elif algorithm == 'PRIMS':
            return random.randint(0, len(self.cells) - 1)

    def exist_test(self, xy):
        """Checks if ordered pair exists within maze size.

        Args:
            xy - the ordered pair to check: <tuple> (x, y)

        Returns:
            boolean exists
        """
        x, y = xy
        exists = False

        # check that x and y are within maze bounds
        if self.x_dim > x >= 0 and self.y_dim > y >= 0:
            exists = True

        return exists

    def find_touching(self, space, dist=1):
        """Finds the spaces that touch 'space' separated by 'dist'.

        Args:
            space - the space to base it off of
            dist - distance from 'space' to check

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
            a list of ordered pairs of touching spaces that exist
        """
        x, y = space
        directions = [(x, y - dist), (x + dist, y), (x, y + dist), (x - dist, y)]

        touching_xy = []
        for dir in directions:
            if self.exist_test(dir):
                touching_xy += [dir]

        return touching_xy

    def paths_only(self, spaces):
        """Filters out all wall spaces from a list of spaces."""

        path_spaces = []
        for space in spaces:
            x, y = space
            if self.maze[x][y]:
                path_spaces += [space]
        return path_spaces

    def get(self):
        """Returns maze."""
        return self.maze

    def display(self, illum_list=()):
        """Prints maze to terminal or console window."""

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


def main():
    m = Maze(True, 25, 20)
    m.make('PRIMS', '', 0)

if __name__ == "__main__":
    main()
