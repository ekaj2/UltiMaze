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

import os


def get_file():
    return os.path.join(os.path.dirname(__file__), "addon_name.txt")


def get_addon_name():
    with open(get_file(), 'r') as f:
        name = f.read().strip()
    return name


def save_addon_name(name):
    with open(get_file(), 'w') as f:
        print(name, file=f)
