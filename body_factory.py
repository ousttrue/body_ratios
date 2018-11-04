from typing import Tuple, List
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
    armature.show_names = True
    armature.use_mirror_x = True


class BodyRatios:
    def __init__(self, armature: bpy.types.Armature)->None:
        self.height = armature.body_ratios.height_meter
        self.crotch_height_meter = armature.body_ratios.crotch_height_meter
        self.heads = armature.body_ratios.heads
        self.neck_len = armature.body_ratios.neck_meter
        self.leg_interval = armature.body_ratios.leg_interval_meter
        self.shoulder_width = armature.body_ratios.shoulder_width_meter
        self.ankle = armature.body_ratios.ankle_height_meter

        self.head_size = self.height/self.heads
        self.head_height = self.head_size * (self.heads-1)
        self.shoulder_height = self.head_height - self.head_size * self.neck_len
        self.hips_height = self.crotch_height_meter
        self.hips_spine_chest = (self.shoulder_height - self.hips_height)/3

        self.arm_length = self.shoulder_height - self.hips_height

        self.ll = self.leg_interval/2
        self.knee_height = (self.crotch_height_meter - self.ankle) / 2


def set_ratios(armature_object: bpy.types.Object)->None:
    armature = armature_object.data
    body_ratios = BodyRatios(armature)

    with tmp_mode(armature_object, 'EDIT'):

        #
        # hips, spine, chest, neck, head
        #

        # hips
        hips = armature.edit_bones['hips']
        hips.head = (0, 0, body_ratios.hips_height)

        # spine
        spine = armature.edit_bones['spine']
        spine.head = hips.head + \
            mathutils.Vector((0, 0, body_ratios.hips_spine_chest))

        # chest
        chest = armature.edit_bones['chest']
        chest.head = spine.head + \
            mathutils.Vector((0, 0, body_ratios.hips_spine_chest))

        # neck
        neck = armature.edit_bones['neck']
        neck.head = (0, 0, body_ratios.shoulder_height)

        # head
        head = armature.edit_bones['head']
        head.head = (0, 0, body_ratios.head_height)
        head.tail = (0, 0, body_ratios.height)

        def create_LR(name, l_head, r_head)->Tuple[bpy.types.EditBone, bpy.types.EditBone]:
            l = armature.edit_bones[name+'.L']
            l.head = l_head
            r = armature.edit_bones[name+'.R']
            r.head = r_head
            return l, r

        #
        # legs
        #
        create_LR('upper_leg',
                  (body_ratios.ll, 0, body_ratios.hips_height),
                  (-body_ratios.ll, 0, body_ratios.hips_height))
        create_LR('lower_leg',
                  (body_ratios.ll, 0, body_ratios.knee_height),
                  (-body_ratios.ll, 0, body_ratios.knee_height))
        foot_l, foot_r = create_LR('foot',
                                   (body_ratios.ll, 0, body_ratios.ankle),
                                   (-body_ratios.ll, 0, body_ratios.ankle))
        foot_l.tail = (body_ratios.ll, -0.2, 0)
        foot_r.tail = (-body_ratios.ll, -0.2, 0)

        #
        # arms -> fingers
        #
        shoulder_l, shoulder_r = create_LR('shoulder',
                                           (0.05, 0, body_ratios.shoulder_height),
                                           (-0.05, 0, body_ratios.shoulder_height))

        shoulder = mathutils.Vector((body_ratios.shoulder_width/2, 0, 0))
        upper_arm_l, upper_arm_r = create_LR('upper_arm',
                                             shoulder_l.head + shoulder,
                                             shoulder_r.head - shoulder
                                             )

        arm = mathutils.Vector((body_ratios.arm_length/2, 0, 0))
        lower_arm_l, lower_arm_r = create_LR('lower_arm',
                                             upper_arm_l.head + arm,
                                             upper_arm_r.head - arm
                                             )

        hand_l, hand_r = create_LR('hand',
                                   lower_arm_l.head + arm,
                                   lower_arm_r.head - arm
                                   )

        hand = mathutils.Vector((0.1, 0, 0))
        hand_l.tail = hand_l.head + hand
        hand_r.tail = hand_r.head - hand
