import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from bpy.app.handlers import persistent


@persistent
def render_and_leave(dummy):
    # get data that was transferred
    with open(os.path.join(os.path.dirname(__file__), "tile_renderer_data.txt"), 'r') as f:
        reload_file = f.readline().strip()
        append_file = f.readline().strip()
        tiles_path = f.readline().strip()

    print("Rendering:", bpy.data.filepath)
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
            print(bpy.data.filepath, self.filename, mg.tiles_path, file=f, sep='\n', flush=True)

        # open the TileRenderer file, render, then reopen this file
        bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(__file__), 'helper_blends', 'TileRenderer.blend'))

        return {'FINISHED'}
