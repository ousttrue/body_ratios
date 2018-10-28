from typing import Optional
import bpy


def create_human(armature_obj: Optional[bpy.types.Object] = None):
    if armature_obj:
        if armature_obj.type != 'ARMATURE':
            raise Exception('not armature: '+armature_obj.type)
        armature = armature_obj.data
    else:
        # creaet armature
        name = 'human'
        armature = bpy.data.armatures.new(name)
        armature_obj = bpy.data.objects.new(name, armature)

        bpy.context.scene.objects.link(armature_obj)
        armature_obj.select = True
        bpy.context.scene.objects.active = armature_obj
        print('create armature %s' % armature)

    print(armature)


create_human(bpy.context.scene.objects.active)
