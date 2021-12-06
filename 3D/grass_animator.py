bl_info = {
    "name": "Grass Sway",
    "description": "Animates grass blades with wind",
    "author": "Michael Moyal",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Animation > Grass Sway",
    "warning": "",
    "category": "Animation"
}

import bpy
from mathutils import *
from math import *
from bpy.props import *

class AnimationProperty(bpy.types.PropertyGroup):
    
    wind_strength : bpy.props.FloatProperty(
    name = 'Wind Strength',
    description = 'Controls how much the blades of grass are affected by the wind',
    default = 1,
    min = 0,
    max = 5,
    step = 10
    )
    
    angle : bpy.props.IntProperty(
    name = 'Wind Angle',
    description = 'Controls the direction of the wind',
    default = 0,
    step = 100
    )
    
class AnimatorPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_grass_panel"
    bl_label = "Grass Animator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):
        self.layout.label(AnimatorPanel.bl_label)
    

class GrassAnimator(bpy.types.Operator):
    bl_idname = "animation.grass_animator"
    bl_label = "Animate grass"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # This function should generate the wind and turbulence with user selected parameters
        # These include turbulence strength, turbulence size and wind strength
        return {'FINISHED'}
    
    def generate_wind():
        pass
    
classes = [AnimationProperty, AnimatorPanel, GrassAnimator]

def menu_func(self, context):
    self.layout.operator(GrassAnimator.bl_idname)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)
    bpy.types.Scene.wind_properties = PointerProperty(type=AnimationProperty)
        
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_func)