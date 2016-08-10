import bpy
import bmesh

from maze_gen.progress_display import BlenderProgress


def quad_mesh_builder(verts, faces):
    me = bpy.data.meshes.new("mesh")
    ob = bpy.data.objects.new("Maze", me)

    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    me = bpy.context.object.data
    bm = bmesh.new()

    bverts = []
    for v in verts:
        bverts.append(bm.verts.new(v))

    for f in faces:
        bm.faces.new([bverts[f[0]], bverts[f[1]], bverts[f[2]], bverts[f[3]]])

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()  # free and prevent further access


def make_3dmaze(maze):
    """Makes basic 3D maze from python list."""
    debug = bpy.context.user_preferences.addons['maze_gen'].preferences.debug_mode

    bldr_prog = BlenderProgress("3D Maze Gen", debug)
    bldr_prog.start()
    maze_length = len(maze)

    loops = 0

    verts = []
    faces = []

    # iterate over every space in the maze
    for x in range(maze.width):
        for y in range(maze.height):
            if maze.is_path(x, y):
                vert_ind = len(verts)
                verts.append((x - 0.5, -(y + 0.5), 0))  # make these a func for adding a plane...
                verts.append((x + 0.5, -(y + 0.5), 0))  # see if list.append(item) returns the item
                verts.append((x + 0.5, -(y - 0.5), 0))
                verts.append((x - 0.5, -(y - 0.5), 0))

                faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

            else:
                vert_ind = len(verts)
                verts.append((x - 0.5, -(y + 0.5), 1))
                verts.append((x + 0.5, -(y + 0.5), 1))
                verts.append((x + 0.5, -(y - 0.5), 1))
                verts.append((x - 0.5, -(y - 0.5), 1))

                faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

                for i, d in enumerate(maze.find_touching(x, y)):
                    if maze.exist_test(d):
                        if maze.is_path(d[0], d[1]):
                            # check for on x-axis!...y-axis
                            if d[0] == x:
                                y_avg = -((d[1] + y) / 2)
                                vert_ind = len(verts)

                                verts.append((d[0] - 0.5, y_avg, 1))
                                verts.append((d[0] + 0.5, y_avg, 1))
                                verts.append((d[0] + 0.5, y_avg, 0))
                                verts.append((d[0] - 0.5, y_avg, 0))

                                faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

                            else:
                                x_avg = (d[0] + x) / 2
                                vert_ind = len(verts)

                                verts.append((x_avg, -(d[1] - 0.5), 1))
                                verts.append((x_avg, -(d[1] + 0.5), 1))
                                verts.append((x_avg, -(d[1] + 0.5), 0))
                                verts.append((x_avg, -(d[1] - 0.5), 0))

                                faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

            progress = loops / maze_length
            bldr_prog.update(progress)

    quad_mesh_builder(verts, faces)

    bldr_prog.finish()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.normals_make_consistent(inside=True)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
