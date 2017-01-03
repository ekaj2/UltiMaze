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

import webbrowser
from os import path, listdir

from bpy.types import Operator


class ReportABug(Operator):
    bl_label = "Report a Bug"
    bl_idname = "maze_gen.report_bug"
    bl_description = "Opens the bug report page and builds the copies the log files to the clipboard."
    bl_options = {'UNDO'}

    def execute(self, context):
        logs = ""
        logs_folder = path.join(path.dirname(__file__), "logs")
        for filename in listdir(logs_folder):
            if filename.endswith('.log'):
                with open(path.join(logs_folder, filename), 'r') as f:
                    logs += filename + "\n-----------------------\n" + f.read() + "\n=========================\n"
        context.window_manager.clipboard = logs
        webbrowser.open_new_tab("http://info.integrity-sg.com/bugs.html")
        return {'FINISHED'}
