# Copyright 2017 Integrity Software and Games, LLC
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of UltiMaze.
#
# UltiMaze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltiMaze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltiMaze.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import unittest

import maze_tools
from clock import Clock


class TestMaze(unittest.TestCase):
    maxDiff = 10000

    def test_make_base_grid_walls(self):
        maze = maze_tools.Maze(10, 10)
        expected = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.assertEqual(maze.get_maze(), expected)

    def test_make_base_grid_paths(self):
        maze = maze_tools.Maze(10, 10, False)
        expected = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        self.assertEqual(maze.get_maze(), expected)

    def test_make_base_grid_speed(self):
        clock = Clock("Init Maze")
        maze_tools.Maze(2500, 2500)
        result = clock.stop("Init Maze")

        self.assertLessEqual(result, 1)


class TestFindTouchingAndExist(unittest.TestCase):
    maxDiff = 10000

    def test_find_touching_simple(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.find_touching(1, 1)
        expected = [(1, 2), (0, 1), (2, 1), (1, 0)]

        self.assertEqual(result, expected)

    def test_find_touching_dist2(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.find_touching(1, 1, 2)
        expected = [(1, 3), (-1, 1), (3, 1), (1, -1)]

        self.assertEqual(result, expected)

    def test_find_touching_off_the_charts(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.find_touching(1, 1, 10)
        expected = [(1, 11), (-9, 1), (11, 1), (1, -9)]

        self.assertEqual(result, expected)

    def test_exist_test_true(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.exist_test(3, 4)
        expected = True

        self.assertEqual(result, expected)

    def test_exist_test_false_low(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.exist_test(-1, 4)
        expected = False

        self.assertEqual(result, expected)

    def test_exist_test_false_high(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.exist_test(3, 10)
        expected = False

        self.assertEqual(result, expected)

    def test_find_touching_path_dirs_none(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.find_touching_path_dirs(1, 1)
        expected = []

        self.assertEqual(result, expected)

    def test_find_touching_path_dirs_all(self):
        maze = maze_tools.Maze(10, 10)
        for i in range(5):
            for j in range(5):
                maze.make_path(i, j)
        result = maze.find_touching_path_dirs(1, 1)
        expected = ['N', 'W', 'E', 'S']

        self.assertEqual(result, expected)

    def test_find_exist_touching(self):
        maze = maze_tools.Maze(10, 10)
        result = maze.find_exist_touching(0, 0)
        expected = [(1, 0), (0, 1)]

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
