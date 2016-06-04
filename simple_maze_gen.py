"""
Simple maze generation (non-tilebased)

Available Functions:
    console_prog - Displays progress in the console
    make_3Dmaze - Makes basic 3D maze from python list
"""

import sys
from time import time

import bpy


def console_prog(job, progress, total_time="?"):
    """Displays progress in the console.

    Args:
        job - name of the job
        progress - progress as a decimal number
        total_time (optional) - the total amt of time the job
                                took for final display
    """
    length = 20
    block = int(round(length * progress))
    message = "\r{0}: [{1}{2}] {3:.0%}".format(job, "#" * block, "-" * (length - block), progress)
    # progress is complete
    if progress >= 1:
        message = "\r{} DONE IN {} SECONDS{}".format(job.upper(), total_time, " " * 12)
    sys.stdout.write(message)
    sys.stdout.flush()


def make_3dmaze(maze):
    """Makes basic 3D maze from python list.

    Constructs maze by adding primitive planes in 'grid' locations, then
    selecting and extruding wall pieces, and finally removing doubles.

    Args:
        maze - python list in the format:
            [[(space in maze - x, y), is path, is walkable, active path],
            [(space in maze - x, y), is path, is walkable, active path], ...]
    """
    s_time = time()
    bpy.context.window_manager.progress_begin(1, 100)
    genloops = 0
    # create a plane primitive
    bpy.ops.mesh.primitive_plane_add(
        view_align=False,
        enter_editmode=False,
        location=(0, 0, 0),
        layers=(True, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False,
                False))

    # create wall material slot
    bpy.ops.object.material_slot_add()
    bpy.context.object.active_material_index = 0

    # create path material slot
    bpy.ops.object.material_slot_add()
    bpy.context.object.active_material_index = 1

    # toggle editmode
    bpy.ops.object.editmode_toggle()

    # remove all preexisting verts
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')

    double_count = 0
    last_percent = None
    for space in maze:
        x_pos = space[0][0]
        y_pos = space[0][1]
        path = space[1]
        # create, scale, translate a plane primitive
        bpy.ops.mesh.primitive_plane_add(
            radius=0.5,
            view_align=False,
            enter_editmode=False,
            location=(x_pos, -y_pos, 0),
            layers=(True, False, False, False, False, False, False, False,
                    False, False, False, False, False, False, False, False, False,
                    False, False, False))

        # assign path material slot if applicable
        if path:
            bpy.context.object.active_material_index = 1
            bpy.ops.object.material_slot_assign()

        # minor optimization...remove doubles
        if genloops > 2500 and double_count > 1500:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            double_count = 0

        genloops += 1
        double_count += 1

        percent = round((genloops / len(maze)) * 100)
        if percent != last_percent and percent < 100:
            bpy.context.window_manager.progress_update(percent)

            # new print out technique
            console_prog("3D Maze Gen", genloops / len(maze))

        last_percent = percent

    # print out finished job before "Info" from removing doubles
    console_prog("3D Maze Gen", 1, time() - s_time)
    print("\n")

    # remove doubles then extrude based on material selection
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.context.object.active_material_index = 0
    bpy.ops.object.material_slot_select()

    bpy.ops.mesh.extrude_region_move(
        MESH_OT_extrude_region={"mirror": False},
        TRANSFORM_OT_translate={"value": (0, 0, 1),
                                "constraint_axis": (False, False, True),
                                "constraint_orientation": 'NORMAL',
                                "mirror": False,
                                "proportional": 'DISABLED',
                                "proportional_edit_falloff": 'SMOOTH',
                                "proportional_size": 1,
                                "snap": False,
                                "snap_target": 'CLOSEST',
                                "snap_point": (0, 0, 0),
                                "snap_align": False,
                                "snap_normal": (0, 0, 0),
                                "gpencil_strokes": False,
                                "texture_space": False,
                                "remove_on_cancel": False,
                                "release_confirm": False})

    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.select_more()
    bpy.ops.object.material_slot_assign()
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.context.object.active_material_index = 1
    bpy.ops.object.material_slot_assign()

    # toggle editmode
    bpy.ops.object.editmode_toggle()

    # name object 'Maze'
    bpy.context.object.name = "Maze"

    bpy.context.window_manager.progress_end()
