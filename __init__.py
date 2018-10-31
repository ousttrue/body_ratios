import bpy


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


def update_func(self, _context):
    armature = get_parent(self)
    print(armature, self)


class BodyRatios(bpy.types.PropertyGroup):
    height_meter = bpy.props.FloatProperty(name="HeightMeter",
                                           description="",
                                           default=1.6,
                                           min=0.1,
                                           max=2.0,
                                           soft_min=1.0,
                                           soft_max=1.9,
                                           step=3,
                                           precision=2,
                                           # options={'ANIMATABLE'},
                                           # subtype='NONE',
                                           unit='LENGTH',
                                           update=update_func,
                                           # get=None,
                                           # set=None
                                           )
    crotch_height_meter = bpy.props.FloatProperty(name="CrotchHeightMeter")


"""
class BodyRatiosPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_body_ratios"
    bl_label = "body ratios"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Body Ratios"

    @classmethod
    def poll(cls, _context):
        for o in bpy.data.objects:
            if o.select:
                return True
        return False

    def draw_header(self, _context):
        self.layout.label(text="xxx", icon='PLUGIN')

    def draw(self, context):
        self.layout.label(text="Hello World")
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.prop(obj, "hide_select")
        row.prop(obj, "hide_render")

        box = layout.box()
        box.label("Selection Tools")
        box.operator("object.select_all").action = 'TOGGLE'
        row = box.row()
        row.operator("object.select_all").action = 'INVERT'
        row.operator("object.select_random")
"""

REGISTER_CLASSES = [
    BodyRatios
]


def register():
    for c in REGISTER_CLASSES:
        bpy.utils.register_class(c)

    bpy.types.Armature.body_ratios = bpy.props.PointerProperty(
        type=BodyRatios,
        update=update_func)


def unregister():
    for c in REGISTER_CLASSES:
        del bpy.types.Armature.body_ratios

    bpy.utils.unregister_module(c)


if __name__ == "__main__":
    register()
