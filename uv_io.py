import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
import bmesh
import json
import os


bl_info = {
    "name": "UV IO",
    "author": "Expenses",
    "version": (0, 0, 1),
    "category": "UV",
    "description": "Saving and loading UVs to a .json file"
}


def get_image_size():
    if bpy.data.images:
        return bpy.data.images[0].size
    else:
        return (1024, 1024)


class LoadUV(bpy.types.Operator, ImportHelper):
    bl_idname = "uv_io.load_uv"
    bl_label = "Load a UV"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    def execute(self, context):
        if not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "'%s' does not exist." % self.filepath)
            return {'CANCELLED'}

        try:
            with open(self.filepath) as json_file:
                verts = json.loads(json_file.read())
        except:
            self.report({'ERROR'}, "json file could not be read")
            return {'CANCELLED'}

        obj = context.active_object

        if obj.type != "MESH":
            self.report({'ERROR'}, "Object type is not mesh.")
            return {'CANCELLED'}

        width, height = get_image_size()

        bpy.ops.object.mode_set(mode='EDIT')
        mesh = bmesh.from_edit_mesh(obj.data)
        uv_layer = mesh.loops.layers.uv.verify()

        for i, face in enumerate(mesh.faces):
            for j, loop in enumerate(face.loops):
                u, v = verts[i][j]
                loop[uv_layer].uv = (u / width, v / height)

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}


class SaveUV(bpy.types.Operator, ExportHelper):
    bl_idname = "uv_io.save_uv"
    bl_label = "Save a UV"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    def execute(self, context):
        obj = context.active_object

        if obj.type != "MESH":
            self.report({'ERROR'}, "Object type is not mesh.")
            return {'CANCELLED'}

        width, height = get_image_size()

        bpy.ops.object.mode_set(mode='EDIT')
        mesh = bmesh.from_edit_mesh(obj.data)
        uv_layer = mesh.loops.layers.uv.verify()

        faces = []

        for face in mesh.faces:
            verts = []

            for loop in face.loops:
                u, v = loop[uv_layer].uv
                verts.append((u * width, v * height))
            faces.append(verts)

        open(self.filepath, "w").write(json.dumps(faces))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(LoadUV)
    bpy.utils.register_class(SaveUV)


def unregister():
    bpy.utils.unregister_class(LoadUV)
    bpy.utils.unregister_class(SaveUV)


if __name__ == "__main__":
    register()
