import plateaupy
import numpy as np
import open3d as o3d

if __name__ == '__main__':
	bLoadCache = False		# set it True after the first run
	#location = 533925
	location = 533945

	# load
	pl = plateaupy.plparser(['../CityGML_01','../CityGML_02'])
	pl.loadFiles( bLoadCache=bLoadCache, cachedir='cached', kind=1, location=location)
	
	# target pldem
	dem = pl.dem[location]
	# target mesh
	mesh = dem.meshes[0]

	# get left-top, right-down corners
	low, upp = plateaupy.plutils.convertMeshcodeToLatLon(location)
	low.append(0)
	upp.append(0)
	print( 'meshcode {}, LT={}, RB={}'.format( location, low, upp ) )
	
	# transform mesh.vertices into [0,1]
	vt = plateaupy.plutils.VerticesTransformer( low, upp )
	normvertices = vt.transform( mesh.vertices )

	# test for inv_transform
	if False:
		normvertices = vt.inv_transform( normvertices )
		normvertices = vt.transform( normvertices )

	# replace it to show
	mesh.vertices = normvertices

	# show by Open3D
	print('presenting..')
	window_name = 'test'
	width  = 640
	height = 480
	bgcolor = [1,1,1]
	vis = o3d.visualization.VisualizerWithKeyCallback()
	vis.create_window(window_name=window_name, width=width, height=height)
	vis.get_render_option().background_color = np.asarray(bgcolor)
	vis.get_render_option().mesh_show_back_face = True
	vis.get_render_option().mesh_show_wireframe = True
	vis.get_render_option().show_coordinate_frame = True

	meshes = pl.get_Open3D_TriangleMesh()#color=[0.5,0.5,0.5])
	for mesh in meshes:
		vis.add_geometry(mesh)
	vis.add_geometry( plateaupy.plutils.createOpen3Dbox(size=1) )
	vis.run()
	print('ESC to quit.')
	vis.poll_events()
	vis.update_renderer()
