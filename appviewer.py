import os
import sys
import numpy as np
import argparse
import open3d as o3d

import plateaupy

# argparser
parser = argparse.ArgumentParser(description='plateaupy appviewer')
parser.add_argument('-paths','--paths',help='list of paths to CityGML dirctories',default=['path_to_citygml'],type=str,nargs='*')
parser.add_argument('-cmd','--cmd',help='special command [locations,codelists,dumpmeta]',default='',type=str)
parser.add_argument('-k','--kind',help='gml kind, -1:all, 0:bldg, 1:dem, 2:luse, 3:tran, 4:brid',default=-1,type=int)
parser.add_argument('-loc','--location',help='location index number',default=-1,type=int)
parser.add_argument('-c','--cache',action='store_true', help='use cache data')
parser.add_argument('-cpath','--cachepath',help='cache directory name',default='cached',type=str)
parser.add_argument('-color','--color',help='color',default=None,type=float,nargs=3)
parser.add_argument('-bgcolor','--bgcolor',help='background color',default=[1,1,1],type=float,nargs=3)
parser.add_argument('-lod0','--lod0',action='store_true', help='use LOD0 in bldg.')
parser.add_argument('-lod2texture','--lod2texture',action='store_true', help='show LOD2 texture images (too slow).')
parser.add_argument('-zh','--zeroheight',action='store_true', help='force to set height values as zero.')
parser.add_argument('-qx','--quarterx',help='force to divide mesh area(6) into the quarter. specify None or 0 or 1', default=None, type=int)
parser.add_argument('-qy','--quartery',help='force to divide mesh area(6) into the quarter. specify None or 0 or 1', default=None, type=int)
parser.add_argument('-plypath','--path_write_ply_files',help='path to write plyfiles.',default=None,type=str)
parser.add_argument('-rec','--recfile',help='a record file name without ext.',default=None,type=str)
parser.add_argument('-show_wire','--show_wire',action='store_true', help='show wireframe in polygons.')
args = parser.parse_args()

# scan paths
pl = plateaupy.plparser(args.paths)

# special commands
if args.cmd == 'locations':
	print('locations: ',pl.locations)
	sys.exit(0)
if args.cmd == 'codelists':
	print('codelists: ',pl.codelists)
	sys.exit(0)

# options
options = plateaupy.ploptions()
options.bUseLOD0 = args.lod0
options.bUseLOD2texture = args.lod2texture
options.texturedir = args.cachepath
options.bHeightZero = args.zeroheight
quarter = None
if args.quarterx is not None and args.quartery is not None:
	quarter = (args.quartery, args.quarterx)
options.div6toQuarter = quarter
# load
pl.loadFiles( bLoadCache=args.cache, cachedir=args.cachepath, kind=args.kind, location=args.location, options=options )

# special commands
if args.cmd == 'dumpmeta':
	for obj in pl.bldg.values():
		for building in obj.buildings:
			print(building,'\n')
	sys.exit(0)

# write ply files
if args.path_write_ply_files is not None:
	print('writing ply files into', args.path_write_ply_files)
	os.makedirs( args.path_write_ply_files, exist_ok=True )
	pl.write_Open3D_ply_files(savepath=args.path_write_ply_files, color=args.color)

# show by Open3D
print('presenting..')
print('ESC to quit.')
meshes = pl.get_Open3D_TriangleMesh(color=args.color)

from plateaupy.plvisualizer import Visualizer3D
vi = Visualizer3D()
if args.show_wire:
	vi.vis.get_render_option().mesh_show_wireframe = True
for mesh in meshes:
	vi.vis.add_geometry(mesh)
if args.recfile is not None:
	vi.start_recording(args.recfile)
while True:
	key = vi.wait(1)
	if key == 27:	# ESC
		break
vi.destroy()
