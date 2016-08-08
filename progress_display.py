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


class BlenderProgress():
    def __init__(self, job, debug=True):
        self.job = job
        self.last_percent = None
        self.debug = debug
        self.elapsed_time = 0

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
        self.elapsed_time = time() - self.s_time
        if not self.debug:
            console_prog(self.job, 1, self.elapsed_time)
            print("\n")
        bpy.context.window_manager.progress_end()

    def elapsed_time(self):
        return self.elapsed_time
