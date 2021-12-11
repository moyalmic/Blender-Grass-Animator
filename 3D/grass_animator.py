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


def wind_update_func(self, context):
    wind_properties = context.scene.wind_properties
    context.scene.wind_object.field.strength = wind_properties.wind_strength 
    context.scene.turbulence_object.field.size = (-10 * wind_properties.wind_strength) + 10
    
def angle_update_func(self, context):
    context.scene.wind_object.rotation_euler[2] = context.scene.wind_properties.angle

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
        context.scene.wind_object = bpy.context.active_object
        turbulence_location = (active_obj.location.x, active_obj.location.y-active_obj.scale.y, active_obj.location.z)
        bpy.ops.object.effector_add(type='TURBULENCE', align='WORLD', location=turbulence_location)
        context.scene.turbulence_object = bpy.context.active_object
        context.scene.turbulence_object.field.size = (-10 * wind_properties.wind_strength) + 10
    
    def animate_keyframes(self, context):
        context.scene.turbulence_object.select_set(True)
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

def size_update_func(self, context):
    object_properties = context.scene.object_properties
    context.scene.grass_plane_object.scale = object_properties.plane_size
    
def length_update_func(self, context):
    object_properties = context.scene.object_properties
    context.scene.grass_plane_object.hair_length = object_properties.grass_length
    
def base_width_update_func(self, context):
    object_properties = context.scene.object_properties
    context.scene.grass_plane_object.root_radius = object_properties.grass_base_width   
    
def shape_update_func(self, context):
    object_properties = context.scene.object_properties
    context.scene.grass_plane_object.brownian_factor = object_properties.grass_shape  
    
def clump_update_func(self, context):
    object_properties = context.scene.object_properties
    context.scene.grass_plane_object.clump_factor = object_properties.clumpyness
     
def density_update_func(self, context):
    object_properties = context.scene.object_properties
    particle_settings = context.scene.grass_plane_object.particle_systems[0].settings.name
    bpy.data.particles[particle_settings].count = object_properties.grass_density
        
class ObjectProperty(bpy.types.PropertyGroup):
    
    plane_size : bpy.props.FloatVectorProperty(
    name = 'Plane size',
    description = 'Controls the size of the grass plane',
    default = (5.0, 5.0, 1.0),
    min = 1,
    step = 10,
    update = size_update_func
    )
    
    grass_length : bpy.props.FloatProperty(
    name = 'Grass Length',
    description = 'Controls how long the grass blades are',
    default = 1.5,
    min = 1,
    max = 5,
    step = 1,
    update = length_update_func
    )  
    
    grass_base_width : bpy.props.FloatProperty(
    name = 'Base Width',
    description = 'Controls how wide the base of the brass blades is',
    default = 2,
    min = 1,
    max = 3,
    step = 1,
    update = base_width_update_func
    )
        
    grass_shape : bpy.props.FloatProperty(
    name = 'Grass Shape',
    description = 'Controls how wide the base of the brass blades is',
    default = 0,
    min = 0,
    max = 0.3,
    step = 1,
    update = shape_update_func
    )
    
    clumpyness : bpy.props.FloatProperty(
    name = 'Clumpyness',
    description = 'Controls how spread out the blades of grass are',
    default = 0,
    min = -1.0,
    max = 0,
    step = 1,
    update = clump_update_func
    )
    
    grass_density : bpy.props.IntProperty(
    name = 'Grass Density',
    description = 'Controls how many blades of grass there are',
    default = 500,
    min = 0,
    step = 100,
    update = density_update_func
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
        row.prop(object_properties, "grass_density")
        row = layout.row(align=True)
        row.operator("object.grass_plane")

        
class GrassGenerator(bpy.types.Operator):
    bl_idname = "object.grass_plane"
    bl_label = "Create grass plane"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        self.generate_plane(context)
        return {'FINISHED'}
        
    def generate_plane(self, context):
        object_properties = context.scene.object_properties
        bpy.data.scenes["Scene"].render.hair_type = 'STRIP'
        bpy.ops.mesh.primitive_plane_add(align='WORLD', scale=object_properties.plane_size)
        context.scene.grass_plane_object = bpy.context.active_object
        bpy.ops.object.particle_system_add()
        particle_settings = context.scene.grass_plane_object.particle_systems[0].settings.name
        bpy.data.particles[particle_settings].type = 'HAIR'
        bpy.data.particles[particle_settings].count = object_properties.grass_density
        bpy.data.particles[particle_settings].use_advanced_hair = True
        bpy.data.particles[particle_settings].hair_length = object_properties.grass_length
        bpy.data.particles[particle_settings].root_radius = object_properties.grass_base_width
        bpy.data.particles[particle_settings].brownian_factor = object_properties.grass_shape
        bpy.data.particles[particle_settings].child_type = 'INTERPOLATED'
        bpy.data.particles[particle_settings].child_nbr = 3
        bpy.data.particles[particle_settings].clump_factor = object_properties.clumpyness
        
        
    def average_vector(self, vec):
        acc = 0
        for scalar in range(0, len(vec)):
            acc += scalar
        acc /= len(vec)
        return int(acc)
        
        
    
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
    # Storage for settings needed by the individual generators
    bpy.types.Scene.wind_properties = PointerProperty(type=AnimationProperty)
    bpy.types.Scene.object_properties = PointerProperty(type=ObjectProperty)
    # Storage for objects created by the plugin and allowing access
    bpy.types.Scene.wind_object = PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.turbulence_object = PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.grass_plane_object = PointerProperty(type=bpy.types.Object)
        
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_object_animation.remove(anim_menu_func)
    bpy.types.VIEW3D_MT_mesh_add.remove(grass_menu_func)
    
    
if __name__ == "__main__":
    register()
