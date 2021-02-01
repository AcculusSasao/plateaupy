import os
import sys
import numpy as np
import argparse
import open3d as o3d

import plateaupy

# argparser
parser = argparse.ArgumentParser(description='plateaupy appviewer')
parser.add_argument('-paths','--paths',help='list of paths to CityGML dirctories',default=['../CityGML_01','../CityGML_02'],type=str,nargs='*')
parser.add_argument('-cmd','--cmd',help='special command [locations,dumpmeta]',default='',type=str)
parser.add_argument('-k','--kind',help='gml kind, -1:all, 0:bldg, 1:dem, 2:luse, 3:tran',default=-1,type=int)
parser.add_argument('-loc','--location',help='location index number',default=-1,type=int)
parser.add_argument('-c','--cache',action='store_true', help='use cache data')
parser.add_argument('-cpath','--cachepath',help='cache directory name',default='cached',type=str)
parser.add_argument('-color','--color',help='color',default=None,type=float,nargs=3)
parser.add_argument('-bgcolor','--bgcolor',help='background color',default=[1,1,1],type=float,nargs=3)
parser.add_argument('-lod2texture','--lod2texture',action='store_true', help='show LOD2 texture images (too slow).')
parser.add_argument('-plypath','--path_write_ply_files',help='path to write plyfiles',default=None,type=str)
args = parser.parse_args()

# scan paths
pl = plateaupy.plparser(args.paths)

# special commands
if args.cmd == 'locations':
	print('locations: ',pl.locations)
	sys.exit(0)

# load
pl.loadFiles( bLoadCache=args.cache, cachedir=args.cachepath, kind=args.kind, location=args.location, bUseLOD2texture=args.lod2texture )

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
window_name = 'PLATEAUpy viewer'
width  = 640
height = 480
bgcolor = args.bgcolor
vis = o3d.visualization.VisualizerWithKeyCallback()
vis.create_window(window_name=window_name, width=width, height=height)
vis.get_render_option().background_color = np.asarray(bgcolor)
vis.get_render_option().mesh_show_back_face = True
vis.get_render_option().mesh_show_wireframe = True
vis.get_render_option().show_coordinate_frame = True
meshes = pl.get_Open3D_TriangleMesh(color=args.color)
for mesh in meshes:
	vis.add_geometry(mesh)
vis.run()
print('ESC to quit.')
vis.poll_events()
vis.update_renderer()
