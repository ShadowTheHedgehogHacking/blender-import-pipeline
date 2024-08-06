import bpy
import importlib
import os
#dff_importer = importlib.import_module("DragonFF.ops.dff_importer")
dff_importer = importlib.import_module("DragonFF.ops.dff_importer")
from io_scene_sth_mtn import import_sth_bon, import_sth_mtn

### Takes a folder full of .DFF files and Exports them to .glb
### ...with connect_bones false
### ...with Animations Disabled
### ...with Materials Exported

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


input_folder = "C:\\Users\\core\\Desktop\\__TARGET\\BK"
output_folder = "C:\\Users\\core\\Desktop\\__TARGET\\out"

os.makedirs(output_folder, exist_ok=True)
dae_files = [f for f in os.listdir(input_folder) if f.endswith('.DFF')]

apply_bone_names = True
bake_action = False

for dae_file in dae_files:
    input_path = os.path.join(input_folder, dae_file)
    output_path = os.path.join(output_folder, os.path.splitext(dae_file)[0] + '.glb')
    cleanup()

    ### DFF Import ###

    options = {
        'file_name'      : input_path,
        'image_ext'      : 'PNG',
        'load_txd'       : False,
        'txd_file_name'  : '',
        'skip_mipmaps'   : False,
        'connect_bones'  : False,
        'use_mat_split'  : False,
        'remove_doubles' : False,
        'group_materials': False,
        'import_normals' : True
    }

    dff_importer.import_dff(options)
    
    # check if BON exists, and if yes apply it
    bon_path = os.path.join(input_folder, os.path.splitext(dae_file)[0] + '.BON')
    if os.path.exists(bon_path):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                obj.select_set(True)
        bpy.ops.import_scene.sth_bon(filepath=bon_path, apply_bone_names=apply_bone_names)
    
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_animations=False,
        export_materials='EXPORT'
    )

cleanup()