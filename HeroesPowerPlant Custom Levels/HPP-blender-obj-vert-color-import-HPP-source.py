### --- HeroesPowerPlant vertex colored OBJ importer for Blender
### ----- Tested on Blender 4.5.5
### ----- Based on Shadowth117's heavily altered 3DSMax script from Chris Cookson's original import script
### --- Use to export .OBJ to Heroes Power Plant with proper vertex colors from the .OBJ import.

import bpy
import bmesh
import os
import math

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

def create_material(mtl_data, base_path):
    mat_name = mtl_data.get('name', 'Material')
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output.location = (400, 0)
    node_principled.location = (0, 0)
    links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

    kd = mtl_data.get('Kd', (0.8, 0.8, 0.8))
    node_principled.inputs['Base Color'].default_value = (kd[0], kd[1], kd[2], 1.0)

    if 'map_Kd' in mtl_data:
        tex_path = os.path.join(base_path, mtl_data['map_Kd'])
        if os.path.exists(tex_path):
            img_node = nodes.new(type='ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(tex_path)
            img_node.location = (-600, 0)
            
            mix_node = nodes.new(type='ShaderNodeMix')
            mix_node.data_type = 'RGBA'
            mix_node.blend_type = 'MULTIPLY'
            mix_node.inputs[0].default_value = 1.0 
            mix_node.location = (-300, 0)
            
            attr_node = nodes.new(type='ShaderNodeAttribute')
            attr_node.attribute_name = "Imported Colors"
            attr_node.location = (-600, -250)
            
            links.new(img_node.outputs['Color'], mix_node.inputs[6])
            links.new(attr_node.outputs['Color'], mix_node.inputs[7])
            links.new(mix_node.outputs[2], node_principled.inputs['Base Color'])
            
    return mat

def load_mtl(filepath):
    materials = {}
    if not os.path.exists(filepath): return materials
    current_mtl = None
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            if parts[0] == 'newmtl':
                current_mtl = parts[1]
                materials[current_mtl] = {'name': current_mtl}
            elif current_mtl and parts[0] == 'Kd':
                materials[current_mtl]['Kd'] = [float(x) for x in parts[1:4]]
            elif current_mtl and parts[0] == 'map_Kd':
                materials[current_mtl]['map_Kd'] = parts[1]
    return materials

def read_obj_file(context, filepath, use_90_rotation, use_uv_flip):
    base_dir = os.path.dirname(filepath)
    verts, uvs, colors, faces = [], [], [], []
    material_libs, face_materials = [], []
    active_mat = None

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            if parts[0] == 'mtllib':
                material_libs.append(parts[1])
            elif parts[0] == 'usemtl':
                active_mat = parts[1]
            elif parts[0] == 'v':
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == 'vt':
                u, v = float(parts[1]), float(parts[2])
                uvs.append((u, -v if use_uv_flip else v))
            elif parts[0] == 'vc':
                colors.append([float(x)/255.0 for x in parts[1:5]])
            elif parts[0] == 'f':
                face_dat = []
                for p in parts[1:]:
                    sub = p.split('/')
                    face_dat.append((int(sub[0])-1, int(sub[1])-1 if len(sub)>1 and sub[1] else None))
                faces.append(face_dat)
                face_materials.append(active_mat)

    mesh_name = os.path.splitext(os.path.basename(filepath))[0]
    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(mesh_name, mesh)
    context.collection.objects.link(obj)

    if use_90_rotation:
        obj.rotation_euler[0] = math.radians(90)

    mesh.from_pydata(verts, [], [[v[0] for v in f] for f in faces])
    
    loaded_mats = {}
    for lib in material_libs:
        mtl_dict = load_mtl(os.path.join(base_dir, lib))
        for m_name, m_data in mtl_dict.items():
            blender_mat = create_material(m_data, base_dir)
            mesh.materials.append(blender_mat)
            loaded_mats[m_name] = len(mesh.materials) - 1

    for i, poly in enumerate(mesh.polygons):
        mat_name = face_materials[i]
        if mat_name in loaded_mats:
            poly.material_index = loaded_mats[mat_name]

    if colors:
        color_attr = mesh.attributes.new(name="Imported Colors", type='FLOAT_COLOR', domain='POINT')
        color_attr.data.foreach_set("color", [c for col in colors for c in col])
        mesh.attributes.active = color_attr

    if uvs:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for i, poly in enumerate(mesh.polygons):
            for loop_idx, vert_data in zip(poly.loop_indices, faces[i]):
                if vert_data[1] is not None:
                    uv_layer.data[loop_idx].uv = uvs[vert_data[1]]

    mesh.validate()
    return {'FINISHED'}


class ImportVC_OBJ(Operator, ImportHelper):
    bl_idname = "import_scene.vc_obj"
    bl_label = "Import VColor OBJ"
    filename_ext = ".obj"

    use_90_rotation: BoolProperty(
        name="90° X Rotation",
        description="Apply 90 degree rotation to the object transform",
        default=True,
    )
    
    use_uv_flip: BoolProperty(
        name="Flip UV Vertical",
        default=False,
    )

    def execute(self, context):
        return read_obj_file(context, self.filepath, self.use_90_rotation, self.use_uv_flip)

def menu_func_import(self, context):
    self.layout.operator(ImportVC_OBJ.bl_idname, text="Vertex Colored OBJ (.obj)")

def register():
    bpy.utils.register_class(ImportVC_OBJ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ImportVC_OBJ)

if __name__ == "__main__":
    register()