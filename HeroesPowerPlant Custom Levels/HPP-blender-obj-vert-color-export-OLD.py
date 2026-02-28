### --- HeroesPowerPlant vertex colored OBJ exporter for Blender
### ----- Tested on Blender 4.5.5
### ----- Exports in the format expected by Shadowth117's heavily altered 3DSMax script from Chris Cookson's original import script

import bpy
import os
import math

def write_obj_with_vc(context, filepath, apply_90_fix):
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return {'CANCELLED'}

    mesh = obj.to_mesh()
    mtl_path = filepath.replace(".obj", ".mtl")
    mtl_filename = os.path.basename(mtl_path)

    with open(filepath, 'w') as f:
        f.write(f"# Exported from Blender\n")
        f.write(f"mtllib {mtl_filename}\n")

        colors = None
        if "Imported Colors" in mesh.attributes:
            colors = mesh.attributes["Imported Colors"].data
        
        for i, v in enumerate(mesh.vertices):
            x, y, z = v.co
            if apply_90_fix and math.isclose(obj.rotation_euler[0], math.radians(90), abs_tol=0.001):
                pass 

            f.write(f"v {v.co.x:.6f} {v.co.y:.6f} {v.co.z:.6f}\n")
            
            if colors:
                col = colors[i].color
                r, g, b, a = [int(c * 255) for c in col]
                f.write(f"vc {r} {g} {b} {a}\n")

        uv_layer = mesh.uv_layers.active
        if uv_layer:
            for loop in mesh.loops:
                uv = uv_layer.data[loop.index].uv
                f.write(f"vt {uv.x:.6f} {uv.y:.6f}\n")

        last_mat = None
        for poly in mesh.polygons:
            if len(obj.material_slots) > 0:
                mat = obj.material_slots[poly.material_index].name
                if mat != last_mat:
                    f.write(f"usemtl {mat}\n")
                    last_mat = mat

            face_verts = []
            for loop_idx in poly.loop_indices:
                v_idx = mesh.loops[loop_idx].vertex_index + 1
                uv_idx = loop_idx + 1
                face_verts.append(f"{v_idx}/{uv_idx}")
            
            f.write(f"f {' '.join(face_verts)}\n")

    with open(mtl_path, 'w') as f_mtl:
        for slot in obj.material_slots:
            mat = slot.material
            if not mat: continue
            f_mtl.write(f"newmtl {mat.name}\n")
            f_mtl.write("Ka 0.2 0.2 0.2\n")
            f_mtl.write("Kd 0.8 0.8 0.8\n")
            f_mtl.write("Ks 0.0 0.0 0.0\n")
            f_mtl.write("Ns 10\n")
            f_mtl.write("d 1.0\n")
            f_mtl.write("illum 4\n")
            
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        f_mtl.write(f"map_Kd {os.path.basename(node.image.filepath)}\n")
                        break

    obj.to_mesh_clear()
    return {'FINISHED'}

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

class ExportVC_OBJ(Operator, ExportHelper):
    bl_idname = "export_scene.vc_obj"
    bl_label = "Export VColor OBJ"
    filename_ext = ".obj"

    def execute(self, context):
        return write_obj_with_vc(context, self.filepath, True)

def menu_func_export(self, context):
    self.layout.operator(ExportVC_OBJ.bl_idname, text="Vertex Colored OBJ (.obj)")

def register():
    bpy.utils.register_class(ExportVC_OBJ)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

if __name__ == "__main__":
    register()