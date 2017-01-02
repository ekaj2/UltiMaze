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
import logging

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from bpy.app.handlers import persistent

from maze_gen import utils
from maze_gen.logging_setup import setup_logger


setup_logger(__name__)


@persistent
def render_and_leave(dummy):
    logger = logging.getLogger(__name__)

    # get data that was transferred
    with open(os.path.join(os.path.dirname(__file__), "tile_renderer_data.txt"), 'r') as f:
        logger.debug("Reading tile_renderer_data.txt")
        reload_file = f.readline().strip()
        append_file = f.readline().strip()
        tiles_path = f.readline().strip()
        samples = int(f.readline().strip())

    # import the one with a suffix?
    logger.debug("Importing:{}".format(append_file))
    utils.append_objs(append_file, suffix="_", ignore="NEVER IGNORE ANYTHING HERE!123@#$%^&*()_!")

    # there may have been more than 1, so remove them if so
    i = 0
    chosen = None
    logger.debug("TileRenderer.blend has the following objects after appending: {}".format([a.name for a in bpy.context.scene.objects]))
    for obj in bpy.context.scene.objects:
        if obj.name.endswith("_"):
            i += 1
            if i > 1:
                obj.select = True
            else:
                chosen = obj

    if chosen is not None:
        chosen.select = False
        # delete selected objects
        bpy.ops.object.delete(use_global=False)

        # move the chosen object to the correct rotation and position and scale
        if append_file.endswith("2.blend"):
            logger.debug("append_file is a 12 tile blend")
            chosen.location = (0, 0, 0.501)
        elif append_file.endswith("6.blend"):
            logger.debug("append_file is a 6 tile blend")
            chosen.location = (0, 0, 0.001)
            chosen.select = True
            bpy.ops.transform.resize(value=(0.6, 0.6, 0.6))
        else:
            logger.error("File did not end with 12 or 6; can't classify; this may cause problems with the TileRenderer.blend file.")

        chosen.rotation_euler = (0, 0, 0)
    else:
        bpy.data.objects['_ORIGINAL_Text'].hide_render = False

    logger.debug("Rendering:{}".format(bpy.data.filepath))
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.render.filepath = os.path.join(tiles_path, append_file[:-6] + ".png")
    bpy.ops.render.render(write_still=True)

    # remove the handler
    logger.debug("Removing the handler")
    bpy.app.handlers.load_post.remove(render_and_leave)

    logger.debug("Loading the original file:{}".format(reload_file))
    bpy.ops.wm.open_mainfile(filepath=reload_file)


class RenderTileSet(Operator):
    bl_label = "YOU MAY LOSE UNSAVED WORK!"
    bl_idname = "maze_gen.render_tileset"
    bl_description = "Opens a .blend file to save out custom tile images.\nYOU MAY LOSE UNSAVED WORK!"
    bl_options = {'UNDO'}

    filename = StringProperty(name="File Name")
    has_png = BoolProperty(name="Blend Has PNG")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        addon_prefs = context.user_preferences.addons['maze_gen'].preferences
        logger = logging.getLogger(__name__)

        mg = context.scene.mg
        logger.debug("Rendering:{}".format(self.filename))
        bpy.ops.wm.save_mainfile()

        # tell blender what to do when the file is loaded
        logger.debug("Appending the 'render_and_leave' function to the load_post handler.")
        bpy.app.handlers.load_post.append(render_and_leave)

        # save data to a text file to reference in the called function
        with open(os.path.join(os.path.dirname(__file__), "tile_renderer_data.txt"), 'w') as f:
            logger.debug("Writing to tile_renderer_data.txt")
            print(bpy.data.filepath, self.filename, addon_prefs.tiles_path, addon_prefs.preview_samples, file=f, sep='\n', flush=True)

        # open the TileRenderer file which will trigger the handler to execute the render_and_leave function
        logger.debug("Opening the TileRenderer.blend file. TODO - add a try/except here for if the file exists")
        bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(__file__), 'helper_blends', 'TileRenderer.blend'))

        return {'FINISHED'}
