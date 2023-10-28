import bpy

import os
from DragonFF.ops import dff_importer
from io_scene_sth_mtn import import_sth_bon, import_sth_mtn

dff_path = "C:\\Users\\user\\Desktop\\shad\\SHADOW_BODY.DFF"
bon_path = "C:\\Users\\user\\Desktop\\shad\\SH.BON"
mtn_directory = "C:\\Users\\user\\Desktop\\shad\\BODY_MTN"
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
bake_action = True

### DFF Import ###

dff_importer.import_dff(options)


### BON Import ###

# select the armature
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        obj.select_set(True)
        
# Ensure you are in Object mode
bpy.ops.object.mode_set(mode='OBJECT')

arm_obj = bpy.context.view_layer.objects.active

if not arm_obj or type(arm_obj.data) != bpy.types.Armature:
    bpy.context.window_manager.popup_menu(import_sth_bon.invalid_active_object, title='Error', icon='ERROR')
else:
    bpy.ops.import_scene.sth_bon(filepath=bon_path, apply_bone_names=apply_bone_names)
    

### MTN Import ###

bpy.ops.object.select_all(action='DESELECT')

def find_bon_root_armature(collection):
    for obj in collection.objects:
        print("Top Level: " + str(obj))
        if obj.name == "bon_root":
            return obj
        children = [child for child in bpy.context.scene.objects if child.parent == obj]
        return find_bon_root_armature(children)
    return None

# Start the search from the root level collections
for collection in bpy.data.collections:
    bon_root_armature = find_bon_root_armature(collection)
    if bon_root_armature:
        print("FOUND!")
        # Set the armature as the active object
        bpy.context.view_layer.objects.active = bon_root_armature

        # Select the armature
        bon_root_armature.select_set(True)
        break

if not bon_root_armature:
    bpy.context.window_manager.popup_menu(import_sth_bon.invalid_active_object, title='Error', icon='ERROR')

bpy.ops.import_scene.sth_mtn(filepath=mtn_directory+"\\"+mtns[0], bake_action=bake_action)