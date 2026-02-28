import bpy

current_obj = bpy.context.object
bpy.ops.object.mode_set(mode="POSE")

current_pose_bones = bpy.context.object.pose

for bone in current_pose_bones.bones:
    bpy.context.object.data.bones.active = bone.bone
    bone.bone.select = True
    bpy.ops.constraint.apply(constraint="Copy Transforms", owner='BONE')
    bone.bone.select = False

bpy.ops.object.mode_set(mode="OBJECT")