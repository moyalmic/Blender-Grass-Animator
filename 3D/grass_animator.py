bl_info = {
    "name": "Grass Sway",
    "description": "Animates grass blades with wind",
    "author": "Michael Moyal",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Animation > Animate Grass",
    "warning": "",
    "category": "Animation"
}

import bpy
from mathutils import *
from math import *
from bpy.props import *


turbulence = None
wind = None
grass_plane = None


def wind_update_func(self, context):
    wind_properties = context.scene.wind_properties
    wind.field.strength = wind_properties.wind_strength 
    turbulence.field.size = (-10 * wind_properties.wind_strength) + 10
    
def angle_update_func(self, context):
    wind.rotation_euler[2] = context.scene.wind_properties.angle

class AnimationProperty(bpy.types.PropertyGroup):
    
    wind_strength : bpy.props.FloatProperty(
    name = 'Wind Strength',
    description = 'Controls how much the blades of grass are affected by the wind',
    default = 0.5,
    min = 0,
    max = 1,
    step = 1,
    update = wind_update_func
    )
    
    angle : bpy.props.IntProperty(
    name = 'Wind Angle',
    description = 'Controls the direction of the wind',
    default = 0,
    step = 100,
    update = angle_update_func
    )
    
class AnimatorPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_grass_anim_panel"
    bl_label = "Grass Animator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):      
        layout = self.layout
        scene = context.scene
        wind_properties = scene.wind_properties
        
        row = layout.row(align=True)
        row.prop(wind_properties, "wind_strength")
        row = layout.row(align=True)
        row.prop(wind_properties, "angle")
        row = layout.row(align=True)
        row.operator("animation.grass_animator")
    

class GrassAnimator(bpy.types.Operator):
    bl_idname = "animation.grass_animator"
    bl_label = "Animate grass"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        self.grass_plane = context.active_object
        self.generate_wind(context, self.grass_plane)
        self.animate_keyframes(context)
        bpy.ops.screen.animation_play()
        return {'FINISHED'}
    
    def generate_wind(self, context, active_obj):
        wind_properties = context.scene.wind_properties
        bpy.ops.object.effector_add(type='WIND',radius=wind_properties.wind_strength, align='CURSOR', 
        rotation=(-90.0, 0.0, wind_properties.angle))
        wind = bpy.data.objects['Wind']
        turbulence_location = (active_obj.location.x, active_obj.location.y-active_obj.scale.y, active_obj.location.z)
        bpy.ops.object.effector_add(type='TURBULENCE', align='WORLD', location=turbulence_location)
        turbulence = bpy.data.objects['Turbulence']
        turbulence.field.size = (-10 * wind_properties.wind_strength) + 10
    
    def animate_keyframes(self, context):
        turbulence.select_set(True)
        bpy.context.object.keyframe_insert(data_path='location', frame=0)
        plane = self.grass_plane
        context.active_object.location.y += plane.scale.y * 2
        bpy.context.object.keyframe_insert(data_path='location', frame=bpy.data.scenes["Scene"].frame_end)

        
        self.set_keyframe_interpolation(context, 'LINEAR')
           
    def set_keyframe_interpolation(self, context, itp_type):
        bpy.context.area.type = 'DOPESHEET_EDITOR'
        bpy.ops.action.interpolation_type(type=itp_type)
        bpy.context.area.type = 'VIEW_3D'
        
# ------------------------------------------------------------------------------------------------------        
        
class ObjectProperty(bpy.types.PropertyGroup):
    
    plane_size : bpy.props.FloatVectorProperty(
    name = 'Plane size',
    description = 'Controls the size of the grass plane',
    default = (1.0, 1.0, 1.0),
    min = 1,
    step = 10
    # update = 
    )
    
    grass_length : bpy.props.FloatProperty(
    name = 'Grass Length',
    description = 'Controls how long the grass blades are',
    default = 1.5,
    min = 1,
    max = 5,
    step = 1
    # update = 
    )  
    
    grass_base_width : bpy.props.FloatProperty(
    name = 'Base Width',
    description = 'Controls how wide the base of the brass blades is',
    default = 2,
    min = 1,
    max = 3,
    step = 1
    # update =
    )
        
    grass_shape : bpy.props.FloatProperty(
    name = 'Grass Shape',
    description = 'Controls how wide the base of the brass blades is',
    default = 0,
    min = 0,
    max = 0.3,
    step = 1
    # update =
    )
    
    clumpyness : bpy.props.FloatProperty(
    name = 'Clumpyness',
    description = 'Controls how spread out the blades of grass are',
    default = 0,
    min = -1.0,
    max = 0,
    step = 1
    # update =
    )
    
        
class GeneratorPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_grass_generate_panel"
    bl_label = "Grass Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):      
        layout = self.layout
        scene = context.scene
        object_properties = scene.object_properties
        
        row = layout.row(align=True)
        row.prop(object_properties, "plane_size")
        row = layout.row(align=True)
        row.prop(object_properties, "grass_length")
        row = layout.row(align=True)
        row.prop(object_properties, "grass_base_width")
        row = layout.row(align=True)
        row.prop(object_properties, "grass_shape")
        row = layout.row(align=True)
        row.prop(object_properties, "clumpyness")
        row = layout.row(align=True)
        row.operator("object.grass_plane")

        
class GrassGenerator(bpy.types.Operator):
    bl_idname = "object.grass_plane"
    bl_label = "Create grass plane"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        self.generate_plane(context)
        
    def generate_plane(self, context):
        object_properties = context.scene.object_properties
        bpy.data.scenes["Scene"].render.hair_type = 'STRIP'
        bpy.ops.mesh.primitive_plane_add(scale=object_properties.plane_size)
        bpy.ops.object.particle_system_add()
        bpy.data.particles["ParticleSettings"].type = 'HAIR'
        # TODO Make this next line take the average of all 3 dimensions and multiply by 10
        bpy.data.particles["ParticleSettings"].count = 500
        bpy.data.particles["ParticleSettings"].use_advanced_hair = True
        bpy.data.particles["ParticleSettings"].hair_length = object_properties.grass_length
        bpy.data.particles["ParticleSettings"].root_radius = object_properties.grass_base_width
        bpy.data.particles["ParticleSettings"].brownian_factor = object_properties.grass_shape
        bpy.data.particles["ParticleSettings"].child_type = 'INTERPOLATED'
        bpy.data.particles["ParticleSettings"].child_nbr = 3
        bpy.data.particles["ParticleSettings"].clump_factor = object_properties.clumpyness
        
        
    
classes = [AnimationProperty, AnimatorPanel, GrassAnimator, ObjectProperty, GeneratorPanel, GrassGenerator]


def anim_menu_func(self, context):
    self.layout.operator(GrassAnimator.bl_idname)
    
def grass_menu_func(self, context):
    self.layout.operator(GrassGenerator.bl_idname)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_object_animation.append(anim_menu_func)
    bpy.types.VIEW3D_MT_mesh_add.append(grass_menu_func)
    bpy.types.Scene.wind_properties = PointerProperty(type=AnimationProperty)
    bpy.types.Scene.object_properties = PointerProperty(type=ObjectProperty)
        
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_object_animation.remove(anim_menu_func)
    bpy.types.VIEW3D_MT_mesh_add.remove(grass_menu_func)
    
    
if __name__ == "__main__":
    register()
    
