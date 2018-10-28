from typing import Optional, Tuple
import json
import pathlib
import contextlib

import bpy
import mathutils  # pylint: disable=E0401


@contextlib.contextmanager
def tmp_mode(obj: bpy.types.Object, mode: str):
    bpy.context.scene.objects.active = obj
    tmp = obj.mode
    print('enter %s mode' % mode)
    bpy.ops.object.mode_set(mode=mode)
    try:
        yield
    finally:
        bpy.context.scene.objects.active = obj
        print('restore %s mode' % tmp)
        bpy.ops.object.mode_set(mode=tmp)


def create_human(armature_obj: Optional[bpy.types.Object] = None):
    # read config
    config_file = pathlib.Path(
        bpy.data.filepath).absolute().parent / 'config.json'
    with config_file.open() as r:
        config = json.load(r)

    # get armature
    if armature_obj:
        if armature_obj.type != 'ARMATURE':
            raise Exception('not armature: '+armature_obj.type)
        armature = armature_obj.data
    else:
        # create armature
        name = 'human'
        armature = bpy.data.armatures.new(name)
        armature_obj = bpy.data.objects.new(name, armature)

        bpy.context.scene.objects.link(armature_obj)
        armature_obj.select = True
        bpy.context.scene.objects.active = armature_obj
        print('create armature %s' % armature)

    with tmp_mode(armature_obj, 'EDIT'):
        # clear
        bones = [b for b in armature.edit_bones]
        for b in bones:
            armature.edit_bones.remove(b)

        height = config['height']
        heads = config['heads']
        neck_len = config['neck_len']
        leg_interval = config['leg_interval']
        shoulder_width = config['shoulder_width']
        ankle = config['ankle']

        head_size = height/heads
        head_height = head_size * (heads-1)
        shoulder_height = head_height - head_size * neck_len
        hips_height = height/2
        hips_spine_chest = (shoulder_height - hips_height)/3

        arm_length = shoulder_height - hips_height

        ll = leg_interval/2
        knee_height = ankle + (height/2 - ankle)/2

        #
        # hips, spine, chest, neck, head
        #

        # hips
        hips = armature.edit_bones.new('hips')
        hips.head = (0, 0, hips_height)

        # spine
        spine = armature.edit_bones.new('spine')
        spine.use_connect = True
        spine.parent = hips
        spine.head = hips.head + mathutils.Vector((0, 0, hips_spine_chest))

        # chest
        chest = armature.edit_bones.new('chest')
        chest.use_connect = True
        chest.parent = spine
        chest.head = spine.head + mathutils.Vector((0, 0, hips_spine_chest))

        # neck
        neck = armature.edit_bones.new('neck')
        neck.use_connect = True
        neck.parent = chest
        neck.head = (0, 0, shoulder_height)

        # head
        head = armature.edit_bones.new('head')
        head.use_connect = True
        head.parent = neck
        head.head = (0, 0, head_height)
        head.tail = (0, 0, height)

        def create_LR(name, use_connect,
                      l_parent, l_head,
                      r_parent, r_head)->Tuple[bpy.types.EditBone, bpy.types.EditBone]:
            l = armature.edit_bones.new(name+'.L')
            l.use_connect = use_connect
            l.parent = l_parent
            l.head = l_head
            r = armature.edit_bones.new(name+'.R')
            r.use_connect = use_connect
            r.parent = r_parent
            r.head = r_head
            return l, r

        #
        # legs
        #
        upper_leg_l, upper_leg_r = create_LR(
            'upper_leg', False,
            hips, (ll, 0, hips_height),
            hips, (-ll, 0, hips_height))
        lower_leg_l, lower_leg_r = create_LR(
            'lower_leg', True,
            upper_leg_l, (ll, 0, knee_height),
            upper_leg_r, (-ll, 0, knee_height))
        foot_l, foot_r = create_LR(
            'foot', True,
            lower_leg_l, (ll, 0, ankle),
            lower_leg_r, (-ll, 0, ankle))
        foot_l.tail = (ll, -0.2, 0)
        foot_r.tail = (-ll, -0.2, 0)

        #
        # arms -> fingers
        #
        shoulder_l, shoulder_r = create_LR(
            'shoulder', False,
            chest, (0.05, 0, shoulder_height),
            chest, (-0.05, 0, shoulder_height))

        shoulder = mathutils.Vector((shoulder_width/2, 0, 0))
        upper_arm_l, upper_arm_r = create_LR(
            'upper_arm', True,
            shoulder_l, shoulder_l.head + shoulder,
            shoulder_r, shoulder_r.head - shoulder
        )

        arm = mathutils.Vector((arm_length/2, 0, 0))
        lower_arm_l, lower_arm_r = create_LR(
            'lower_arm', True,
            upper_arm_l, upper_arm_l.head + arm,
            upper_arm_r, upper_arm_r.head - arm
        )

        hand_l, hand_r = create_LR(
            'hand', True,
            lower_arm_l, lower_arm_l.head + arm,
            lower_arm_r, lower_arm_r.head - arm
        )

        hand = mathutils.Vector((0.1, 0, 0))
        hand_l.tail = hand_l.head + hand
        hand_r.tail = hand_r.head - hand

    armature.show_names = True
    armature.use_mirror_x = True


create_human(bpy.context.scene.objects.active)
