import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from bpy.app.handlers import persistent

from maze_gen import utils


@persistent
def render_and_leave(dummy):
    # get data that was transferred
    with open(os.path.join(os.path.dirname(__file__), "tile_renderer_data.txt"), 'r') as f:
        reload_file = f.readline().strip()
        append_file = f.readline().strip()
        tiles_path = f.readline().strip()
        samples = int(f.readline().strip())

    # import the one with a suffix?
    print("Importing:", append_file)
    utils.append_objs(append_file, suffix="_", ignore="NEVER IGNORE ANYTHING HERE!123@#$%^&*()_!")

    # there may have been more than 1, so remove them if so
    i = 0
    chosen = None
    print([a for a in bpy.context.scene.objects])
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
            print("ends with a 2")
            chosen.location = (0, 0, 0.501)
        elif append_file.endswith("6.blend"):
            print("ends with a 6")
            chosen.location = (0, 0, 0.001)
            chosen.select = True
            bpy.ops.transform.resize(value=(0.6, 0.6, 0.6))
        else:
            print("This should be logged (in render_kit.py)...")

        chosen.rotation_euler = (0, 0, 0)
    else:
        bpy.data.objects['_ORIGINAL_Text'].hide_render = False

    print("Rendering:", bpy.data.filepath)
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.render.filepath = os.path.join(tiles_path, append_file[:-6] + ".png")
    bpy.ops.render.render(write_still=True)

    # remove the handler
    bpy.app.handlers.load_post.remove(render_and_leave)

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
        mg = context.scene.mg
        print("Rendering:", self.filename)
        bpy.ops.wm.save_mainfile()

        # tell blender what to do when the file is loaded
        bpy.app.handlers.load_post.append(render_and_leave)

        # save data to a text file to reference in the called function
        with open(os.path.join(os.path.dirname(__file__), "tile_renderer_data.txt"), 'w') as f:
            print(bpy.data.filepath, self.filename, mg.tiles_path, mg.preview_samples, file=f, sep='\n', flush=True)

        # open the TileRenderer file, render, then reopen this file
        bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(__file__), 'helper_blends', 'TileRenderer.blend'))

        return {'FINISHED'}
