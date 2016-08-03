IN_BLENDER = True

import random

if IN_BLENDER:
    from maze_gen import weira
    from maze_gen.progress_display import BlenderProgress
else:
    import weira
    from time import sleep


def round_avg(x1, x2):
    return round((x1 + x2) / 2)


class OrthogonalMaze:
    """Flexible and powerful grid-based maze generation class.

    Methods:
        __init__ - Initializes variables, creates maze grid, starts progress report, makes maze, ends progress report.
        make_base_grid - Sets up self.maze with grid based on x and y dimension args.
        make - Makes a maze.
        start_location - Generates random, even x and y values.
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

    def __init__(self, debug, width=10, height=10):
        """Initializes variables, creates maze grid, starts progress report, makes maze, ends progress report."""
        global IN_BLENDER
        self.IN_BLENDER = IN_BLENDER

        self.debug = debug
        self.width = width
        self.height = height

        self.maze = []
        self.cells = []
        self.loops = 0
        self.estimated_loops = int((self.width * self.height * 1.25))

        self.make_base_grid()

        if self.IN_BLENDER:
            self.bldr_prog = BlenderProgress("Layout Gen", self.debug)
            self.bldr_prog.start()

        self.make()

        if self.IN_BLENDER:
            self.bldr_prog.finish()

    def make_base_grid(self):
        """Sets up self.maze with grid based on x and y dimension args."""
        for column in range(0, self.width):
            self.maze += [[]]
            for row in range(0, self.height):
                self.maze[column] += [0]

    def make(self):
        """Makes a maze. Only a stub."""

        # generate random, but even x and y start location
        x, y = self.start_location()
        self.cells += [(x, y)]
        self.maze[x][y] = 1

        while self.cells:
            index = self.choose_ind()
            x, y = self.ordered_pair(index)

            directions = self.get_directions(x, y)
            directions = self.shuffle_directions(directions)
            for dx, dy in directions:

                # check that we're not by more than 1 path cell
                if self.limited_paths_check((dx, dy), 1):
                    continue

                if self.exist_test((dx, dy)) and self.maze[dx][dy] == 0:
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

            self.loop_update()

    def start_location(self):
        """Generates random, even x and y values."""
        return random.randint(0, int((self.width - 1) / 2)) * 2, random.randint(0, int((self.height - 1) / 2)) * 2

    def shuffle_directions(self, directions):
        return random.shuffle(directions)

    @staticmethod
    def get_directions(x, y):
        """Returns a list of the spaces from 4 directions 2 spaces from given ordered pair."""
        return [(x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)]

    @staticmethod
    def dir_to_ordered_pair(x, y, direction, dist=2):
        """Returns ordered pair of direction."""
        if direction == 'N':
            return x, y - dist
        elif direction == 'E':
            return x + dist, y
        elif direction == 'S':
            return x, y + dist
        elif direction == 'W':
            return x - dist, y
        else:
            print("Error! Invalid direction!")

    def loop_update(self, sleep_time=0.0):
        """Updates progress reports."""
        if self.IN_BLENDER:
            self.loops += 1
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
        if self.width > x >= 0 and self.height > y >= 0:
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

        # x-axis labels
        tens_digit = [str([b for b in range(10)][int(a / 10)]) for a in range(self.width)]
        disp = "    " + "".join(tens_digit).replace("0", " ") + "\n"
        ones_digit = [str([b for b in range(10)][a % 10]) for a in range(self.width)]
        disp += "    " + "".join(ones_digit) + "\n"
        # x-axis arrows
        disp += "   " + "v" * (self.width + 2) + "\n"

        for y in range(self.height):
            # y-axis labels and arrows
            disp += "{:2d}".format(y) + " >"
            for x in range(self.width):
                # illuminated are shown with '$'
                if (x, y) in illum_list:
                    disp += "$"
                # paths are shown with ' '
                elif self.maze[x][y]:
                    disp += " "
                # walls are shown with '#'
                else:
                    disp += "#"
            # right-hand y-axis arrows and newlines
            disp += "<\n"

        # bottom x-axis arrows
        disp += "   " + "^" * (self.width + 2)
        print(disp)


class PassageCarverMaze(OrthogonalMaze):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GraphTheoryMaze(PassageCarverMaze):
    def __init__(self, bias_direction, bias, **kwargs):
        self.bias_direction = bias_direction
        self.bias = bias
        super().__init__(**kwargs)

    def shuffle_directions(self, directions):
        if self.bias_direction == 'RANDOM':
            bias_direction = random.choice(['X', 'Y'])
        else:
            bias_direction = self.bias_direction

        if bias_direction == 'X':
            w_dirs = list(zip(directions, [0, 0, 1, 1]))
        elif bias_direction == 'Y':
            w_dirs = list(zip(directions, [1, 1, 0, 0]))
        else:
            w_dirs = list(zip(directions, [1, 1, 1, 1]))
        return weira.weira_shuffle(w_dirs, self.bias)


class BreadthFirstMaze(GraphTheoryMaze):
    def choose_ind(self):
        return 0


class DepthFirstMaze(GraphTheoryMaze):
    def choose_ind(self):
        return len(self.cells) - 1


class PrimsMaze(GraphTheoryMaze):
    def choose_ind(self):
        return random.randint(0, len(self.cells) - 1)


# just a stub
class KruskalsMaze(GraphTheoryMaze):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BinaryTreeMaze(PassageCarverMaze):
    def __init__(self, directions='RANDOM', tileable=False, **kwargs):

        # parse 'directions' to make tuple
        if directions == 'NE':
            self.directions = ['N', 'E']
        elif directions == 'NW':
            self.directions = ['N', 'W']
        elif directions == 'SE':
            self.directions = ['S', 'E']
        elif directions == 'SW':
            self.directions = ['S', 'W']
        else:
            possible_dirs = [['N', 'E'], ['N', 'W'], ['S', 'E'], ['S', 'W']]
            self.directions = random.choice(possible_dirs)

        self.tileable = tileable

        super().__init__(**kwargs)

    def make(self):
        # start in top, left corner
        for x in range(self.width)[::2]:
            for y in range(self.height)[::2]:

                d = ''
                # this controls how we handle the edges
                if self.tileable:
                    self.maze[x][y] = 1
                    d = random.choice(self.directions)
                else:
                    temp_directions = []

                    self.maze[x][y] = 1

                    # y-axis
                    if y > 0 and 'N' in self.directions:
                        temp_directions += 'N'
                    elif y < self.height - 1 and 'S' in self.directions:
                        temp_directions += 'S'

                    # x-axis
                    if x > 0 and 'W' in self.directions:
                        temp_directions += 'W'
                    elif x < self.width - 1 and 'E' in self.directions:
                        temp_directions += 'E'

                    # choose direction
                    if temp_directions:
                        d = random.choice(temp_directions)
                if d:
                    nx, ny = self.dir_to_ordered_pair(x, y, d, 1)
                    if self.exist_test((nx, ny)):
                        self.maze[nx][ny] = 1

                self.loop_update()


# just a stub
class EllersGridMaze(PassageCarverMaze):
    def __init__(self, junct_random_fac=0, **kwargs):
        self.junct_random_fac = junct_random_fac
        super().__init__(**kwargs)


def main():
    # BinaryTreeMaze('NW', debug=True, width=33, height=23)
    DepthFirstMaze(bias_direction='Y', bias=0.5, debug=True, width=35, height=21)

if __name__ == "__main__":
    main()
