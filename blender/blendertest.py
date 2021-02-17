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
options = plateaupy.ploptions()
##################

# scan paths
pl = plateaupy.plparser(paths)

# load
pl.loadFiles( bLoadCache=cache, cachedir=cachepath, kind=kind, location=location, options=options )

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
