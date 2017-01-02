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

import bpy
import os


def append_objs(path, prefix="", suffix="", case_sens=False, ignore="IGNORE"):
    """Appends all objects into scene from .blend if they meet argument criteria."""

    scene = bpy.context.scene

    with bpy.data.libraries.load(path) as (data_from, data_to):
        if not case_sens:
            data_to.objects = [name for name in data_from.objects if
                               name.lower().startswith(prefix.lower()) and name.lower().endswith(suffix.lower()) and ignore.upper() not in name.upper()]
        else:
            data_to.objects = [name for name in data_from.objects if name.startswith(prefix) and name.endswith(suffix) and ignore.upper() not in name.upper()]

    for obj in data_to.objects:
        if obj is not None:
            scene.objects.link(obj)


def make_absolute(key):
    addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences
    if key in addon_prefs and addon_prefs[key].startswith('//'):
        # must use a[x] notation instead of a.x so it doesn't trigger update callbacks infinitely
        addon_prefs[key] = os.path.abspath(bpy.path.abspath(addon_prefs[key]))
