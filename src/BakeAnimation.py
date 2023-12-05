import bpy


def bake():
    armature = bpy.data.objects["Armature"]
    action = armature.animation_data.action
    scene = bpy.context.scene

    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        fcurveValue = {}
        for group in action.groups:
            for fcurve in group.channels:
                fcurveValue[(fcurve.data_path, fcurve.array_index)] = fcurve.evaluate(frame)

        for (data_path, index), value in fcurveValue.items():
            bpy.context.object.keyframe_insert(data_path, index=index, frame=frame)
