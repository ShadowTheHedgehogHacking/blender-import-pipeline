### --- HeroesPowerPlant vertex colored OBJ exporter for Blender

import bpy
import os
import math

def extract_vertex_colors(mesh):
    attr = None
    
    if "Imported Colors" in mesh.color_attributes:
        attr = mesh.color_attributes["Imported Colors"]
    elif "Imported Colors" in mesh.attributes:
        attr = mesh.attributes["Imported Colors"]
    elif mesh.color_attributes.active_color:
        attr = mesh.color_attributes.active_color
    elif len(mesh.color_attributes) > 0:
        attr = mesh.color_attributes[0]
    else:
        for a in mesh.attributes:
            if a.data_type in {'BYTE_COLOR', 'FLOAT_COLOR'}:
                attr = a
                break

    if not attr:
        return None

    if attr.domain == 'POINT':
        return [tuple(datum.color[:4]) if len(datum.color) >= 4 else (*datum.color[:3], 1.0) for datum in attr.data]

    elif attr.domain == 'CORNER':
        v_count = len(mesh.vertices)
        temp_colors = [[0.0, 0.0, 0.0, 0.0] for _ in range(v_count)]
        counts = [0 for _ in range(v_count)]

        for loop_idx, loop in enumerate(mesh.loops):
            v_idx = loop.vertex_index
            c = attr.data[loop_idx].color
            t = temp_colors[v_idx]
            t[0] += c[0]
            t[1] += c[1]
            t[2] += c[2]
            t[3] += c[3] if len(c) > 3 else 1.0
            counts[v_idx] += 1

        final_colors = []
        for i in range(v_count):
            count = counts[i]
            if count > 0:
                fac = 1.0 / count
                t = temp_colors[i]
                final_colors.append((t[0]*fac, t[1]*fac, t[2]*fac, t[3]*fac))
            else:
                final_colors.append((1.0, 1.0, 1.0, 1.0))
        return final_colors

    return None

def write_obj_with_vc(context, filepath, export_selected, apply_90_fix):
    if export_selected:
        obs = [o for o in context.selected_objects if o.type == 'MESH']
    else:
        obs = [o for o in context.scene.objects if o.type == 'MESH']

    if not obs:
        return {'CANCELLED'}

    mtl_path = filepath.replace(".obj", ".mtl")
    mtl_filename = os.path.basename(mtl_path)
    
    v_offset = 1
    vt_offset = 1
    exported_materials = {}

    with open(filepath, 'w') as f:
        f.write(f"# Exported from Blender 4.5\n")
        f.write(f"mtllib {mtl_filename}\n")

        for obj in obs:
            depsgraph = context.evaluated_depsgraph_get()
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            
            f.write(f"\no {obj.name}\n") 

            colors = extract_vertex_colors(mesh)
            
            for i, v in enumerate(mesh.vertices):
                if apply_90_fix and math.isclose(obj.rotation_euler[0], math.radians(90), abs_tol=0.001):
                    rot_fix = Matrix.Rotation(math.radians(-90), 4, 'X')
                    world_coord = obj.matrix_world @ rot_fix @ v.co
                else:
                    world_coord = obj.matrix_world @ v.co
                f.write(f"v {world_coord.x:.6f} {world_coord.y:.6f} {world_coord.z:.6f}\n")
                
                if colors:
                    col = colors[i] 
                    r, g, b = [int(max(0, min(1, c)) * 255) for c in col[:3]]
                    a = int(max(0, min(1, col[3])) * 255) if len(col) > 3 else 255
                    f.write(f"vc {r} {g} {b} {a}\n")

            uv_layer = mesh.uv_layers.active
            if uv_layer:
                for loop in mesh.loops:
                    uv = uv_layer.data[loop.index].uv
                    f.write(f"vt {uv.x:.6f} {uv.y:.6f}\n")
            else:
                for _ in mesh.loops:
                    f.write("vt 0.000000 0.000000\n")

            last_mat = None
            for poly in mesh.polygons:
                if len(obj.material_slots) > 0:
                    mat_slot = obj.material_slots[poly.material_index]
                    if mat_slot.material:
                        mat_name = mat_slot.material.name
                        if mat_name != last_mat:
                            f.write(f"usemtl {mat_name}\n")
                            last_mat = mat_name
                        exported_materials[mat_name] = mat_slot.material

                face_verts = []
                for loop_idx in poly.loop_indices:
                    v_idx = (mesh.loops[loop_idx].vertex_index) + v_offset
                    vt_idx = (loop_idx) + vt_offset
                    face_verts.append(f"{v_idx}/{vt_idx}")
                
                f.write(f"f {' '.join(face_verts)}\n")

            v_offset += len(mesh.vertices)
            vt_offset += len(mesh.loops)
            obj.to_mesh_clear()

    with open(mtl_path, 'w') as f_mtl:
        for name, mat in exported_materials.items():
            f_mtl.write(f"newmtl {name}\n")
            f_mtl.write("Ka 1.0 1.0 1.0\nKd 1.0 1.0 1.0\nKs 0.0 0.0 0.0\nd 1.0\nillum 2\n")
            if mat.use_nodes:
                tex = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
                if tex: f_mtl.write(f"map_Kd {os.path.basename(tex.image.filepath)}\n")

    return {'FINISHED'}

from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Matrix

class ExportVC_OBJ(Operator, ExportHelper):
    bl_idname = "export_scene.vc_obj"
    bl_label = "Export VColor OBJ"
    filename_ext = ".obj"

    export_selected: BoolProperty(
        name="Selection Only",
        description="Export only selected mesh objects",
        default=True,
    )

    apply_90_fix: BoolProperty(
        name="Apply 90° X Rotation Fix",
        description="Bake out 90 degree X rotation to coordinates",
        default=True,
    )

    def execute(self, context):
        return write_obj_with_vc(context, self.filepath, self.export_selected, self.apply_90_fix)

def menu_func_export(self, context):
    self.layout.operator(ExportVC_OBJ.bl_idname, text="Vertex Colored OBJ (.obj)")

def register():
    bpy.utils.register_class(ExportVC_OBJ)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportVC_OBJ)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()