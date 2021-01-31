from plateaupy import plutils
import bpy
import plateaupy
import math

if True:
	#reset objects
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(True)
	#world
	bpy.context.scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0,0,0,1)
	#lamp add
	bpy.ops.object.light_add(location=(0.0,0.0,2.0))
	#camera add
	bpy.ops.object.camera_add(location=(5.0,0.0,0.0))
	bpy.data.objects['Camera'].rotation_euler = (math.pi*1/2, 0, math.pi*1/2)

##################
#####  args  #####
##################
paths = ['../CityGML_01','../CityGML_02']
cache = False
cachepath = 'cached_blender'
kind = plateaupy.plobj.ALL
location = 533925
lod2texture = False
##################

# scan paths
pl = plateaupy.plparser(paths)

# load
pl.loadFiles( bLoadCache=cache, cachedir=cachepath, kind=kind, location=location, bUseLOD2texture=lod2texture )

# decide the base point to show
vbase = None
targets = list(pl.dem.values())
if len(targets) > 0:
	vbase = targets[0].get_center_vertices()
targets = list(pl.bldg.values())
if vbase is None and len(targets) > 0:
	vbase = targets[0].get_center_vertices()
targets = list(pl.tran.values())
if vbase is None and len(targets) > 0:
	vbase = targets[0].get_center_vertices()
targets = list(pl.luse.values())
if vbase is None and len(targets) > 0:
	vbase = targets[0].get_center_vertices()

# show
pl.show_Blender_Objects(vbase=vbase)

if False:
	bpy.ops.mesh.primitive_cylinder_add(location=(-5, 5, 0), radius=1, depth=3, rotation=(0, 0, 0))
	bpy.ops.mesh.primitive_cube_add(location=(5, 0, 0), size=1.5, rotation=(0, 0, 0))
	bpy.ops.mesh.primitive_ico_sphere_add(location=(-5, 0, 0), radius=1, subdivisions=5)
	bpy.ops.mesh.primitive_monkey_add(location = (-5, -5, 0), size = 3.0)
	bpy.ops.mesh.primitive_torus_add(location=(0, 5, 0), major_radius=1.0, minor_radius=0.1, rotation=(0, 0, 0))
	bpy.ops.mesh.primitive_circle_add(location=(5, 5, 0), fill_type="NGON", radius=2, rotation=(0, 0, 0))
	bpy.ops.mesh.primitive_plane_add(location=(5, -5, 0), rotation=(0, 0, 0), size=2)
	bpy.ops.mesh.primitive_cone_add(location=(0,-5,0),vertices=10,radius1=0.5,radius2=1,depth=3, rotation=(0, 0, 0))
