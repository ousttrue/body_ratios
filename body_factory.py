from typing import Optional, Tuple, List
import json
import pathlib
import contextlib

import bpy
import mathutils  # pylint: disable=E0401


@contextlib.contextmanager
def tmp_mode(obj: bpy.types.Object, mode: str):
    bpy.context.scene.objects.active = obj
    tmp = None
    if mode != obj.mode:
        tmp = obj.mode
        print('enter %s mode' % mode)
        bpy.ops.object.mode_set(mode=mode)
    try:
        yield
    finally:
        bpy.context.scene.objects.active = obj
        if tmp:
            print('restore %s mode' % tmp)
            bpy.ops.object.mode_set(mode=tmp)


def set_ratios(armature_object: bpy.types.Object)->None:
    with tmp_mode(armature_object, 'EDIT'):
        print('set_ratios')


def delete_bones(armature_object: bpy.types.Object)->None:
    armature = armature_object.data
    with tmp_mode(armature_object, 'EDIT'):
        bones = [b for b in armature.edit_bones]
        for b in bones:
            armature.edit_bones.remove(b)


class Bone:
    def __init__(self, name: str, head: Tuple[float, float, float], *children, **kw)->None:
        self.name = name
        self.head = head
        self.children = children
        self.tail = None
        if 'tail' in kw:
            self.tail = kw['tail']

    def __str__(self)->str:
        if self.tail:
            return '<%s %s %s>' % (self.name, self.head, self.tail)
        else:
            return '<%s %s>' % (self.name, self.head)


ROOT = Bone('hips', (0, 0, 0.8),
            Bone('spine', (0, 0, 1.0),
                 Bone('chest', (0, 0, 1.1),
                      Bone('neck', (0, 0, 1.3),
                           Bone('head', (0, 0, 1.4), tail=(0, 0, 1.6))
                           ),
                      Bone('shoulder.L', (0.04, 0, 1.3),
                           Bone('upper_arm.L', (0.1, 0, 1.3),
                                Bone('lower_arm.L', (0.4, 0, 1.3),
                                     Bone('hand.L', (0.7, 0, 1.3), tail=(0.8, 0, 1.3)
                                          )))),
                      Bone('shoulder.R', (-0.04, 0, 1.3),
                           Bone('upper_arm.R', (-0.1, 0, 1.3),
                                Bone('lower_arm.R', (-0.4, 0, 1.3),
                                     Bone('hand.R', (-0.7, 0, 1.3), tail=(-0.8, 0, 1.3)
                                          ))))
                      )
                 ),
            Bone('upper_leg.L', (0.1, 0, 0.8),
                 Bone('lower_leg.L', (0.1, 0, 0.4),
                      Bone('foot.L', (0.1, 0, 0.1), tail=(0.1, -0.2, 0)
                           ))),
            Bone('upper_leg.R', (-0.1, 0, 0.8),
                 Bone('lower_leg.R', (-0.1, 0, 0.4),
                      Bone('foot.R', (-0.1, 0, 0.1), tail=(-0.1, -0.2, 0)
                           )))
            )


def create_bone(armature: bpy.types.Armature, parent: bpy.types.EditBone, children: List[Bone])->None:
    isFirst = True
    for child_conf in children:
        print(child_conf)
        bone = armature.edit_bones.new(child_conf.name)
        bone.parent = parent
        if isFirst:
            bone.use_connect = True
            isFirst = False
        else:
            bone.use_connect = False
        bone.head = child_conf.head
        if child_conf.tail:
            bone.tail = child_conf.tail

        create_bone(armature, bone, child_conf.children)


def create_bones(armature_object: bpy.types.Object)->None:
    armature = armature_object.data
    with tmp_mode(armature_object, 'EDIT'):
        create_bone(armature, None, [ROOT])


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


if __name__ == '__main__':
    create_human(bpy.context.scene.objects.active)
