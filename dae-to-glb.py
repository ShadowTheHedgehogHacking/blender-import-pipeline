import bpy
import os

### Takes a folder full of .dae files and Exports them to .glb
### ...using the .dae custom normals
### ...with Animations Disabled
### ...with Materials Exported

input_folder = "C:\\Users\\user\\Desktop\\__0600"
output_folder = "C:\\Users\\user\\Desktop\\__0600\\out"

os.makedirs(output_folder, exist_ok=True)
dae_files = [f for f in os.listdir(input_folder) if f.endswith('.dae')]

for dae_file in dae_files:
    input_path = os.path.join(input_folder, dae_file)
    output_path = os.path.join(output_folder, os.path.splitext(dae_file)[0] + '.glb')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    bpy.ops.wm.collada_import(filepath=input_path, custom_normals=True)
    
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_animations=False,
        export_materials='EXPORT'
    )
    
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)