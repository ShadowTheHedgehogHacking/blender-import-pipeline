import bpy

import os
from DragonFF.ops import dff_importer
from io_scene_sth_mtn import import_sth_bon, import_sth_mtn

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    
    
def find_bon_root_armature(collection):
    for obj in collection.objects:
            ## TODO: Find a way to find what to match to, its not necessarily going to match the filename
            ## The target name is always at 0x10 in the .bon file read!
        if obj.name == "DevilDoom.bon":
            return obj
    return None


target_dff_name = "DEVILDOOM.DFF"
dff_parent = "C:\\Users\\user\\Desktop\\_TARGET\\"
dff_path = "C:\\Users\\user\\Desktop\\_TARGET\\" + target_dff_name
bon_path = "C:\\Users\\user\\Desktop\\_TARGET\\DEVILDOOM.BON"
mtn_directory = "C:\\Users\\user\\Desktop\\_TARGET\\MTN"
mtn_output = mtn_directory + "\\out"
os.makedirs(mtn_output, exist_ok=True)
mtns = [f for f in os.listdir(mtn_directory) if f.endswith('.MTN')]

options = {
    'file_name'      : dff_path,
    'image_ext'      : 'PNG',
    'connect_bones'  : False,
    'use_mat_split'  : False,
    'remove_doubles' : False,
    'group_materials': False,
    'import_normals' : True
}

apply_bone_names = True
bake_action = True
create_nla_track = True

cleanup()

### Export once without any mtns

base_model_export = os.path.join(dff_parent, os.path.splitext(target_dff_name)[0] + '.blend')

### DFF Import ###

dff_importer.import_dff(options)

### BON Import ###

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        obj.select_set(True)
bpy.ops.import_scene.sth_bon(filepath=bon_path, apply_bone_names=apply_bone_names)

### Export mtnless model
bpy.ops.wm.save_as_mainfile(filepath=base_model_export)

### Export all mtns separately

for mtn in mtns:
    input_path = os.path.join(mtn_directory, mtn)
    output_path = os.path.join(mtn_output, os.path.splitext(mtn)[0] + '.blend')
    cleanup()

    ### DFF Import ###

    dff_importer.import_dff(options)

    ### BON Import ###

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            obj.select_set(True)
    bpy.ops.import_scene.sth_bon(filepath=bon_path, apply_bone_names=apply_bone_names)
        
    ### MTN Import ###

    bpy.ops.object.select_all(action='DESELECT')

    # Start the search from the root level collections
    for collection in bpy.data.collections:
        bon_root_armature = find_bon_root_armature(collection)
        if bon_root_armature:
            # Set the armature as the active object
            bpy.context.view_layer.objects.active = bon_root_armature

            # Select the armature
            bon_root_armature.select_set(True)
            break

    import_sth_mtn.load(bpy.context, input_path, bake_action, create_nla_track)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)

cleanup()