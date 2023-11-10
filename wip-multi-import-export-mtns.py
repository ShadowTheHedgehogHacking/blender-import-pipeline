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


dff_path = "C:\\Users\\user\\Desktop\\_TARGET\\SHADOW_BODY.DFF"
bon_path = "C:\\Users\\user\\Desktop\\_TARGET\\SH.BON"
mtn_directory = "C:\\Users\\user\\Desktop\\_TARGET\\MTN"
mtns = [f for f in os.listdir(mtn_directory) if os.path.isfile(os.path.join(mtn_directory, f))]

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
bake_action = False

### DFF Import ###

dff_importer.import_dff(options)

### BON Import ###

# select the armature
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        obj.select_set(True)
        
arm_obj = bpy.context.view_layer.objects.active

if not arm_obj or type(arm_obj.data) != bpy.types.Armature:
    bpy.context.window_manager.popup_menu(import_sth_bon.invalid_active_object, title='Error', icon='ERROR')
else:
    bpy.ops.import_scene.sth_bon(filepath=bon_path, apply_bone_names=apply_bone_names)
    

### MTN Import ###

### TODO: Since we know that batch multi-actions do not map correctly in one file, perhaps we should just redo the entire process per DFF from scratch.

bpy.ops.object.select_all(action='DESELECT')

def find_bon_root_armature(collection):
    for obj in collection.objects:
            ## TODO: Find a way to find what to match to, its not necessarily going to match the filename
        if obj.name == "sh.bon":
            return obj
    return None

# Start the search from the root level collections
for collection in bpy.data.collections:
    bon_root_armature = find_bon_root_armature(collection)
    if bon_root_armature:
        # Set the armature as the active object
        bpy.context.view_layer.objects.active = bon_root_armature

        # Select the armature
        bon_root_armature.select_set(True)
        break

for mtn in mtns:
    print(mtn_directory+"\\"+mtn)
    file_path = mtn_directory+"\\"+mtn
    import_sth_mtn.load(bpy.context, file_path, bake_action)