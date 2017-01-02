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

import sys
from time import time

import bpy

from maze_gen.time_display import TimeDisplay


def console_prog(job, progress, total_time="?"):
    """Displays progress in the console.

    Args:
        job - name of the job
        progress - progress as a decimal number
        total_time (optional) - the total amt of time the job took for final display
    """
    length = 20
    block = int(round(length * progress))
    message = "\r{0}: [{1}{2}] {3:.0%}".format(job, "#" * block, "-" * (length - block), progress)
    # progress is complete
    if progress >= 1:
        time_disp = TimeDisplay()
        time_disp.convert(total_time)
        message = "\r{} DONE IN {}                    ".format(job.upper(), time_disp.upper())
    sys.stdout.write(message)
    sys.stdout.flush()


class BlenderProgress:
    def __init__(self, job, debug=True):
        self.job = job
        self.last_percent = None
        self.debug = debug
        self.elapsed_time_bp = 0

        self.s_time = 0

    def start(self):
        self.s_time = time()
        bpy.context.window_manager.progress_begin(0, 100)
        if not self.debug:
            print("\n")

    def update(self, progress):
        percent = progress * 100
        if self.last_percent != percent and percent <= 100:
            bpy.context.window_manager.progress_update(percent)
            if not self.debug:
                console_prog(self.job, progress)
        self.last_percent = percent

    def finish(self):
        self.elapsed_time_bp = time() - self.s_time
        if not self.debug:
            console_prog(self.job, 1, self.elapsed_time_bp)
            print("\n")
        bpy.context.window_manager.progress_end()

    def elapsed_time(self):
        return self.elapsed_time_bp
