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

    def __init__(self, debug, x_dim=10, y_dim=10):
        """Creates maze grid and initializes variables."""
        global IN_BLENDER
        self.IN_BLENDER = IN_BLENDER

        self.debug = debug
        self.x_dim = x_dim
        self.y_dim = y_dim

        self.maze = []
        self.cells = []
        self.loops = 0
        self.estimated_loops = int((self.x_dim * self.y_dim * 1.25))

        for column in range(0, self.x_dim):
            self.maze += [[]]
            for row in range(0, self.y_dim):
                self.maze[column] += [0]

        if self.IN_BLENDER:
            self.bldr_prog = BlenderProgress("Layout Gen", self.debug)
            self.bldr_prog.start()

    def make(self):
        """Makes a maze. Only a stub."""

        x, y = random.randint(0, self.x_dim - 1), random.randint(0, self.y_dim - 1)
        self.cells += [(x, y)]
        self.maze[x][y] = 1

        while self.cells:
            index = self.choose_ind()
            x, y = self.ordered_pair(index)

            directions = self.get_directions(x, y)

            random.shuffle(directions)

            for d in directions:
                dx, dy = d

                # check that we're not by more than 1 path cell
                if self.limited_paths_check((dx, dy), 1):
                    continue

                if self.exist_test(d) and self.maze[d[0]][d[1]] == 0:
                    # space in between b/c we are doing doubles
                    self.maze[self.round_avg(x, dx)][self.round_avg(y, dy)] = 1
                    # space (second one)
                    self.maze[dx][dy] = 1
                    self.cells += [(dx, dy)]
                    index = None
                    break

            # remove from cells list if index has not been found
            if index is not None:
                self.cells.pop(index)

            self.loops += 1
            self.loop_update(index)

        self.finish()

    @staticmethod
    def get_directions(x, y):
        return [(x, y + 2), (x + 2, y), (x, y - 2), (x - 2, y)]

    def loop_update(self, index):
        if self.IN_BLENDER:
            progress = self.loops / self.estimated_loops
            self.bldr_prog.update(progress)
        elif index is None:
            self.display()
            sleep(0.1)

    def finish(self):
        if self.IN_BLENDER:
            self.bldr_prog.finish()

    def ordered_pair(self, index):
        return self.cells[index][0], self.cells[index][1]

    def limited_paths_check(self, space, max_allowed):
        return len(self.paths_only(self.find_touching(space))) > max_allowed

    @staticmethod
    def round_avg(x1, x2):
        return round((x1 + x2) / 2)

    def choose_ind(self):
        """Chooses index...only a stub"""
        return 0

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


class BreadthFirstMaze(Maze):
    def choose_ind(self):
        return 0


class DepthFirstMaze(Maze):
    def choose_ind(self):
        return len(self.cells) - 1


class PrimsMaze(Maze):
    def choose_ind(self):
        return random.randint(0, len(self.cells) - 1)


class DepthPrimsMixMaze(Maze):
    def __init__(self, debug, x_dim, y_dim, mix):
        super(DepthPrimsMixMaze, self).__init__(debug, x_dim, y_dim)
        self.mix = mix

    def choose_ind(self):
        return rand_prob([(0, 1 - self.mix), (len(self.cells) - 1, self.mix)])


def main():
    m = DepthPrimsMixMaze(True, 25, 20, 0)
    m.make()

if __name__ == "__main__":
    main()
