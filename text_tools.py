import bpy


class ReplaceTextMG(bpy.types.Operator):
    bl_label = "Replace Text"
    bl_idname = "maze_gen.replace_text_mg"
    bl_description = "Replaces text1 with text2 in specified textblock"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mg = context.scene.mg

        if not mg.list_maze:
            self.report({'ERROR'}, "List missing! Please assign a " +
                        "valid text data block.")
            return {'CANCELLED'}

        # get text
        str_list_maze = bpy.data.texts[mg.list_maze].as_string()

        # replace text1 with text2
        str_list_maze = str_list_maze.replace(mg.text1_mg, mg.text2_mg)

        # write text
        bpy.data.texts[mg.list_maze].from_string(str_list_maze)

        return {'FINISHED'}


class InvertTextMG(bpy.types.Operator):
    bl_label = "Invert Maze"
    bl_idname = "maze_gen.invert_text_mg"
    bl_description = "Inverts 1s and 0s in specified textblock"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mg = context.scene.mg

        if not mg.list_maze:
            self.report({'ERROR'}, "List missing! Please assign a " +
                        "valid text data block.")
            return {'CANCELLED'}

        # get text
        str_list_maze = bpy.data.texts[mg.list_maze].as_string()

        # replace text1 with text2
        str_list_maze = str_list_maze.replace("1", "_")
        str_list_maze = str_list_maze.replace("0", "1")
        str_list_maze = str_list_maze.replace("_", "0")

        # write text
        bpy.data.texts[mg.list_maze].from_string(str_list_maze)

        return {'FINISHED'}
