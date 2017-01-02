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
import bmesh

from .progress_display import BlenderProgress
from .addon_name import get_addon_name


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


class Make3DMaze:
    def __init__(self, maze):
        self.verts = []
        self.faces = []

        self.make_3dmaze(maze)

    def add_hor_plane(self, x, y, z):
        vert_ind = len(self.verts)
        self.verts.append((x - 0.5, -(y + 0.5), z))
        self.verts.append((x + 0.5, -(y + 0.5), z))
        self.verts.append((x + 0.5, -(y - 0.5), z))
        self.verts.append((x - 0.5, -(y - 0.5), z))

        self.faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

    def make_3dmaze(self, maze):
        """Makes basic 3D maze from python list."""

        debug = bpy.context.user_preferences.addons[get_addon_name()].preferences.debug_mode

        bldr_prog = BlenderProgress("3D Maze Gen", debug)
        bldr_prog.start()
        maze_length = len(maze)

        loops = 0

        # iterate over every space in the maze
        for x in range(maze.width):
            for y in range(maze.height):
                if maze.is_path(x, y):
                    self.add_hor_plane(x, y, 0)

                else:
                    self.add_hor_plane(x, y, 1)

                    for i, d in enumerate(maze.find_touching(x, y)):
                        if maze.exist_test(d[0], d[1]):
                            if maze.is_path(d[0], d[1]):
                                # check for on x-axis!...y-axis
                                if d[0] == x:
                                    y_avg = -((d[1] + y) / 2)
                                    vert_ind = len(self.verts)

                                    self.verts.append((d[0] - 0.5, y_avg, 1))
                                    self.verts.append((d[0] + 0.5, y_avg, 1))
                                    self.verts.append((d[0] + 0.5, y_avg, 0))
                                    self.verts.append((d[0] - 0.5, y_avg, 0))

                                    self.faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

                                else:
                                    x_avg = (d[0] + x) / 2
                                    vert_ind = len(self.verts)

                                    self.verts.append((x_avg, -(d[1] - 0.5), 1))
                                    self.verts.append((x_avg, -(d[1] + 0.5), 1))
                                    self.verts.append((x_avg, -(d[1] + 0.5), 0))
                                    self.verts.append((x_avg, -(d[1] - 0.5), 0))

                                    self.faces.append([vert_ind, vert_ind + 1, vert_ind + 2, vert_ind + 3])

                progress = loops / maze_length
                bldr_prog.update(progress)

        quad_mesh_builder(self.verts, self.faces)

        bldr_prog.finish()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
