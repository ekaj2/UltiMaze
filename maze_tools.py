IN_BLENDER = False

import random

if IN_BLENDER:
    from maze_gen.random_probability import rand_prob
    from maze_gen.progress_display import BlenderProgress
else:
    from random_probability import rand_prob
    from time import sleep


def round_avg(x1, x2):
    return round((x1 + x2) / 2)


class GridMaze:
    """Flexible and powerful grid-based maze generation class.

    Methods:
        __init__ - Initializes variables, creates maze grid, starts progress report, makes maze, ends progress report.
        make_base_grid - Sets up self.maze with grid based on x and y dimension args.
        make - Makes a maze.
        get_directions - Returns a list of the spaces from 4 directions 2 spaces from given ordered pair.
        dir_to_ordered_pair - Returns ordered pair of direction.
        loop_update - Updates progress reports.
        ordered_pair - Returns the ordered pair of passed index.
        limited_paths_check - Returns True if space is neighboring more than max_allowed spaces, False otherwise.
        choose_ind -  Chooses index...only a stub.
        exist_test - Checks if ordered pair exists within maze size.
        find_touching - Finds the spaces that touch 'space' separated by 'dist'.
        paths_only - Filters out all wall spaces from a list of spaces.
        get - Returns maze.
        display - Prints maze to terminal or console window.
    """

    def __init__(self, debug, x_dim=10, y_dim=10):
        """Initializes variables, creates maze grid, starts progress report, makes maze, ends progress report."""
        global IN_BLENDER
        self.IN_BLENDER = IN_BLENDER

        self.debug = debug
        self.x_dim = x_dim
        self.y_dim = y_dim

        self.maze = []
        self.cells = []
        self.loops = 0
        self.estimated_loops = int((self.x_dim * self.y_dim * 1.25))

        self.make_base_grid()

        if self.IN_BLENDER:
            self.bldr_prog = BlenderProgress("Layout Gen", self.debug)
            self.bldr_prog.start()

        self.make()

        if self.IN_BLENDER:
            self.bldr_prog.finish()

    def make_base_grid(self):
        """Sets up self.maze with grid based on x and y dimension args."""
        for column in range(0, self.x_dim):
            self.maze += [[]]
            for row in range(0, self.y_dim):
                self.maze[column] += [0]

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
                    self.maze[round_avg(x, dx)][round_avg(y, dy)] = 1
                    # space (second one)
                    self.maze[dx][dy] = 1
                    self.cells += [(dx, dy)]
                    index = None
                    break

            # remove from cells list if index has not been found
            if index is not None:
                self.cells.pop(index)

            self.loops += 1
            self.loop_update(0.1)

    @staticmethod
    def get_directions(x, y):
        """Returns a list of the spaces from 4 directions 2 spaces from given ordered pair."""
        return [(x, y + 2), (x + 2, y), (x, y - 2), (x - 2, y)]

    @staticmethod
    def dir_to_ordered_pair(x, y, direction, dist=2):
        """Returns ordered pair of direction."""
        if direction == 'N':
            return x, y + dist
        elif direction == 'E':
            return x + dist, y
        elif direction == 'S':
            return x, y - dist
        elif direction == 'W':
            return x - dist, y

    def loop_update(self, sleep_time=0):
        """Updates progress reports."""
        if self.IN_BLENDER:
            progress = self.loops / self.estimated_loops
            self.bldr_prog.update(progress)
        else:
            self.display()
            if sleep_time:
                sleep(sleep_time)

    def ordered_pair(self, index):
        """Returns the ordered pair of passed index."""
        return self.cells[index][0], self.cells[index][1]

    def limited_paths_check(self, space, max_allowed):
        """Returns True if space is neighboring more than max_allowed spaces, False otherwise."""
        return len(self.paths_only(self.find_touching(space))) > max_allowed

    def choose_ind(self):
        """Chooses index...only a stub."""
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

        disp = "v" * (self.x_dim + 2) + "\n"
        for y in range(self.y_dim):
            disp += ">"
            for x in range(self.x_dim):
                if (x, y) in illum_list:
                    disp += "$"
                elif self.maze[x][y]:
                    disp += " "
                else:
                    disp += "#"
            disp += "<\n"
        disp += "^" * (self.x_dim + 2)
        print(disp)


class BreadthFirstGridMaze(GridMaze):
    def choose_ind(self):
        return 0


class DepthFirstGridMaze(GridMaze):
    def choose_ind(self):
        return len(self.cells) - 1


class PrimsGridMaze(GridMaze):
    def choose_ind(self):
        return random.randint(0, len(self.cells) - 1)


class BinaryTreeGridMaze(GridMaze):
    def __init__(self, debug, x_dim, y_dim, directions='RANDOM'):

        # parse 'directions' to make tuple
        if directions == 'NE':
            self.directions = ('N', 'E')
        elif directions == 'NW':
            self.directions = ('N', 'W')
        elif directions == 'SE':
            self.directions = ('S', 'E')
        elif directions == 'SW':
            self.directions = ('S', 'W')
        else:
            possible_dirs = [('N', 'E'), ('N', 'W'), ('S', 'E'), ('S', 'W')]
            self.directions = random.choice(possible_dirs)

        super().__init__(debug, x_dim, y_dim)

    def make(self):
        # start in top, left corner
        for x in range(self.x_dim)[::2]:
            for y in range(self.y_dim)[::2]:
                self.maze[x][y] = 1

                d = random.choice(self.directions)
                nx, ny = self.dir_to_ordered_pair(x, y, d, 1)
                if self.exist_test((nx, ny)):
                    self.maze[nx][ny] = 1

                self.loop_update()


def main():
    BinaryTreeGridMaze(True, 25, 20)

if __name__ == "__main__":
    main()
