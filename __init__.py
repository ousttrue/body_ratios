import importlib
import bpy
from . import body_factory
importlib.reload(body_factory)


bl_info = {
    "name": "body ratios",
    "description": "humanoid skeleton utility",
    "author": "ousttrue",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "Armature",
    "support": "COMMUNITY",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object"
}


def get_parent(self):
    path = '.'.join(repr(self).split('.')[0:-1])
    return eval(path)  # pylint: disable=W0123


def update_func(self, context):
    armature = get_parent(self)
    #print(armature, self)
    # build
    if armature == context.active_object.data:
        body_factory.set_ratios(context.active_object, armature)
    else:
        print('%s is not %s' % (context.active_object.data, armature))


class BodyRatios(bpy.types.PropertyGroup):
    height_meter = bpy.props.FloatProperty(name="HeightMeter",
                                           description="",
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
    crotch_height_meter = bpy.props.FloatProperty(name="CrotchHeightMeter",
                                                  default=0.8,
                                                  precision=2,
                                                  unit='LENGTH',
                                                  update=update_func)


class BodyRatiosPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_body_ratios"
    bl_label = "body ratios"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Body Ratios"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if not active:
            return False
        if active.type != 'ARMATURE':
            return False
        return True

    def draw_header(self, _context):
        self.layout.label(text="Body Ratios", icon='PLUGIN')

    def draw(self, context):
        active_object = context.active_object

        # delete bones
        row = self.layout.row()

        # settings
        row = self.layout.row()
        self.layout.prop(active_object.data.body_ratios, "height_meter")
        self.layout.prop(active_object.data.body_ratios, "crotch_height_meter")

        # build human
        row = self.layout.row()

        """
        box = layout.box()
        box.label("Selection Tools")
        box.operator("object.select_all").action = 'TOGGLE'
        row = box.row()
        row.operator("object.select_all").action = 'INVERT'
        row.operator("object.select_random")
        """


REGISTER_CLASSES = [
    BodyRatios,
    BodyRatiosPanel
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
        bpy.utils.unregister_module(c)


if __name__ == "__main__":
    register()
