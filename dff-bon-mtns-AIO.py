### Export all-in-one dff/bon/mtns pairings in glb; Initial working revision by Psycrow101
### Note: Use multi-mesh branch when dealing with complex models (ex Devil Doom) -> download latest, rename the contents of the zip as "DragonFF", rezip, then import the addon.

### Warning DAE does not properly export all animations currently, use GLB (default) instead.

import bpy

import os
from DragonFF.ops import dff_importer
from io_scene_sth_mtn import import_sth_mtn

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def convert_mtn_aio(dff_options, bon_options, mtn_options, mtns_path, output_path, to_glb):
    # Import
    dff_importer.import_dff(dff_options)
    bpy.ops.import_scene.sth_bon(**bon_options)

    for mtn in mtns_path:
        import_sth_mtn.load(bpy.context, mtn, mtn_options['bake_action'])

    # Remove BON
    for o in bpy.context.scene.objects:
        if o.get("bon_model_name") is not None:
            bpy.data.objects.remove(o, do_unlink=True)

    # Remove BON actions
    for act in bpy.data.actions:
        if "baked_" not in act.name:
            bpy.data.actions.remove(act, do_unlink=True)

    # Rename baked actions
    for act in bpy.data.actions:
        act.name = act.name.replace("baked_", "")       

    # Export
    if (to_glb):
        bpy.ops.export_scene.gltf(
            filepath=output_path+".glb",
            export_animations=True,
            export_materials='EXPORT'
        )
    else:
        bpy.ops.wm.collada_export(filepath=output_path+".dae")
    
# TODO: Find a way to have a filepicker or something to specify paths
dff_path = "C:\\Users\\core\\Desktop\\__TARGET\\supershadow\\SUPERSHADOW.DFF"
bon_path = "C:\\Users\\core\\Desktop\\__TARGET\\supershadow\\SH.BON"
mtn_directory = "C:\\Users\\core\\Desktop\\__TARGET\\supershadow\\SUPERSHADOW"
mtns_path = [os.path.join(mtn_directory, f) for f in os.listdir(mtn_directory) if f.endswith('.MTN')]
output_directory = mtn_directory + "\\out"
os.makedirs(output_directory, exist_ok=True)
output_path = os.path.join(output_directory, "AIO_SuperShadow")

dff_options = {
    'file_name'      : dff_path,
    'image_ext'      : 'PNG',
    'connect_bones'  : False,
    'use_mat_split'  : False,
    'remove_doubles' : False,
    'group_materials': False,
    'import_normals' : True
}

bon_options = {
    'filepath'         : bon_path,
    'apply_bone_names' : True
}

mtn_options = {
    'bake_action'      : True,
}

to_glb = True # Change to false for DAE export instead

cleanup()
convert_mtn_aio(dff_options, bon_options, mtn_options, mtns_path, output_path, to_glb)