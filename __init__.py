IS_RELOAD = 'bpy' in globals()

import importlib
import bpy
from . import body_factory

if IS_RELOAD:
    importlib.reload(body_factory)


bl_info = {
    'name': 'body ratios',
    'description': 'humanoid skeleton utility',
    'author': 'ousttrue',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'Armature',
    'support': 'COMMUNITY',
    'warning': 'This addon is still in development.',
    'wiki_url': '',
    'category': 'Object'
}


def get_parent(self):
    path = '.'.join(repr(self).split('.')[0:-1])
    return eval(path)  # pylint: disable=W0123


def update_func(self, context):
    armature = get_parent(self)
    #print(armature, self)
    # build
    if armature == context.active_object.data:
        body_factory.set_ratios(context.active_object)
    else:
        print('%s is not %s' % (context.active_object.data, armature))


class BodyRatios(bpy.types.PropertyGroup):
    height_meter = bpy.props.FloatProperty(
        name='HeightMeter',
        description='',
        default=1.6,
        min=0.1,
        max=2.0,
        soft_min=1.0,
        soft_max=1.9,
        step=1,
        precision=2,
        # options={'ANIMATABLE'},
        # subtype='NONE',
        unit='LENGTH',
        update=update_func,
        # get=None,
        # set=None
    )
    crotch_height_meter = bpy.props.FloatProperty(
        name='CrotchHeightMeter',
        default=0.8,
        min=0.1,
        max=2.0,
        precision=2,
        step=1,
        unit='LENGTH',
        update=update_func)

    heads = bpy.props.FloatProperty(
        name='TotalHeightHeads',
        default=6,
        min=2,
        max=10,
        precision=1,
        step=10,
        update=update_func)

    neck_meter = bpy.props.FloatProperty(
        name='NeckLengthMeter',
        default=0.1,
        min=0.01,
        max=1,
        precision=2,
        step=1,
        unit='LENGTH',
        update=update_func
    )

    leg_interval_meter = bpy.props.FloatProperty(
        name='LegIntervalMeter',
        default=0.1,
        min=0.01,
        max=1,
        precision=2,
        step=1,
        unit='LENGTH',
        update=update_func)

    shoulder_width_meter = bpy.props.FloatProperty(
        name='ShoulderWidthMeter',
        default=0.3,
        min=0.01,
        max=1,
        precision=2,
        step=1,
        unit='LENGTH',
        update=update_func)

    ankle_height_meter = bpy.props.FloatProperty(
        name='AnkleHeightMeter',
        default=0.1,
        min=0.01,
        max=1,
        precision=2,
        step=1,
        unit='LENGTH',
        update=update_func)


class PollArmature:
    @classmethod
    def poll(cls, context):
        active = context.active_object
        if not active:
            return False
        if active.type != 'ARMATURE':
            return False
        return True


class BodyRatiosDeleteBones(bpy.types.Operator, PollArmature):
    bl_idname = 'body_ratios.delete_bones'
    bl_label = 'delete bones'

    def execute(self, context):
        body_factory.delete_bones(context.active_object)
        return {'FINISHED'}


class BodyRatiosCreateBones(bpy.types.Operator, PollArmature):
    bl_idname = 'body_ratios.create_bones'
    bl_label = 'create bones'

    def execute(self, context):
        body_factory.create_bones(context.active_object)
        body_factory.set_ratios(context.active_object)
        return {'FINISHED'}


class BodyRatiosPanel(bpy.types.Panel, PollArmature):
    bl_idname = 'body_ratios.panel'
    bl_label = 'body ratios'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Body Ratios'

    def draw_header(self, _context):
        self.layout.label(text='Body Ratios', icon='PLUGIN')

    def draw(self, context):
        active_object = context.active_object

        # delete bones
        self.layout.operator('body_ratios.delete_bones')

        # create bones
        self.layout.operator('body_ratios.create_bones')

        # settings
        self.layout.prop(active_object.data.body_ratios, 'height_meter')
        self.layout.prop(active_object.data.body_ratios, 'heads')
        self.layout.prop(active_object.data.body_ratios, 'crotch_height_meter')
        self.layout.prop(active_object.data.body_ratios, 'neck_meter')
        self.layout.prop(active_object.data.body_ratios,
                         'shoulder_width_meter')
        self.layout.prop(active_object.data.body_ratios, 'leg_interval_meter')
        self.layout.prop(active_object.data.body_ratios, 'ankle_height_meter')


REGISTER_CLASSES = [
    BodyRatios,
    BodyRatiosDeleteBones,
    BodyRatiosCreateBones,
    BodyRatiosPanel,
]


def register():
    for c in REGISTER_CLASSES:
        bpy.utils.register_class(c)

    bpy.types.Armature.body_ratios = bpy.props.PointerProperty(
        type=BodyRatios,
        update=update_func)


def unregister():
    if 'body_ratios' in bpy.types.Armature:
        del bpy.types.Armature.body_ratios

    for c in REGISTER_CLASSES:
        try:
            bpy.utils.unregister_class(c)
        except:  # pylint: disable=W0702
            pass


if __name__ == '__main__':
    register()
