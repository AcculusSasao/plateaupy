import os
import numpy as np
from lxml import etree
from plateaupy.plutils import *
import pickle

class plmesh:
	def __init__(self) -> None:
		self.vertices = []	# [ num_of_vertices,  3 ]  (float)
		self.triangles = []	# [ num_of_triangles, 3 ]  (int)
		self.texture_filename = None
		self.triangle_uvs = []			# [ 3 * num_of_triangles, 2 ]  (float)
		self.triangle_material_ids = []	# [ num_of_triangles ]  (int)
	
	def get_center_vertices(self):
		return np.mean( self.vertices, axis=0 )
	
	def to_Open3D_TriangleMesh(self,color=None):
		import open3d as o3d

		mesh = o3d.geometry.TriangleMesh()
		mesh.vertices = o3d.utility.Vector3dVector( self.vertices )
		mesh.triangles = o3d.utility.Vector3iVector( self.triangles )
		if self.texture_filename is not None:
			mesh.textures = [o3d.io.read_image( self.texture_filename )]
			mesh.triangle_uvs = o3d.utility.Vector2dVector( np.array(self.triangle_uvs) )
			mesh.triangle_material_ids = o3d.utility.IntVector( np.array(self.triangle_material_ids, dtype=np.int32) )
			#print( 'triangles = ', np.array(self.triangles).shape )
			#print( 'triangle_uvs = ', np.array(self.triangle_uvs).shape )
			#print( 'triangle_material_ids = ', np.array(self.triangle_material_ids).shape )
		elif color is not None:
			mesh.paint_uniform_color( color )
		mesh.compute_vertex_normals()
		return mesh
	
	def to_Blender_Object(self, meshname, vbase=None):
		import bpy
		
		namestr = meshname
		mesh = bpy.data.meshes.new(name=namestr)
		vertices = [ list(v) for v in self.vertices ]
		triangles = [ list(t) for t in self.triangles ]
		if vbase is not None:
			vertices = [ list(np.array(v) - vbase) for v in vertices ]
		mesh.from_pydata( vertices, [], triangles )
		mesh.update(calc_edges=True)
		obj = bpy.data.objects.new(name=namestr,object_data=mesh)
		return obj

class plobj:
	# kind
	ALL  = -1
	BLDG = 0
	DEM  = 1
	LUSE = 2
	TRAN = 3
	@staticmethod
	def getLocationFromFilename(filename, bLarge=False):
		loc = int(os.path.basename(filename).split('_')[0])
		if bLarge and loc >= 1000000:	# eg. bldg is 53392546, besides dem is 533925
			loc = loc // 100
		return loc
	@staticmethod
	def getCacheFilename(cachedir, filename):
		return cachedir + '/' + os.path.splitext(os.path.basename(filename))[0]

	def __init__(self):
		self.filename = None
		self.location = 0	# location number
		self.lowerCorner = np.zeros((3))	# lowerCorner (lon,lat,height)
		self.upperCorner = np.zeros((3))	# upperCorner
		self.meshes = []	# list of plmesh

	def loadFile(self,filename):
		print('load', filename)
		self.filename = filename
		self.location = self.getLocationFromFilename(filename)
		tree = etree.parse(filename)
		root = tree.getroot()
		# lowerCorner, upperCorner
		vals = tree.xpath('/core:CityModel/gml:boundedBy/gml:Envelope/gml:lowerCorner', namespaces=root.nsmap)
		if len(vals) > 0:
			self.lowerCorner = str2floats(vals[0])
		vals = tree.xpath('/core:CityModel/gml:boundedBy/gml:Envelope/gml:upperCorner', namespaces=root.nsmap)
		if len(vals) > 0:
			self.upperCorner = str2floats(vals[0])
		return tree, root

	def get_Open3D_TriangleMesh(self,color=None):
		_color = color
		if _color is None:
			_color = np.random.rand(3)
		return [ m.to_Open3D_TriangleMesh(_color) for m in self.meshes ]

	def get_Blender_Objects(self, vbase=None):
		rname = randomname(3)
		return [ m.to_Blender_Object(meshname=str(self.location)+'_'+rname+'_'+str(idx),vbase=vbase) for idx,m in enumerate(self.meshes) ]

	def get_center_vertices(self):
		centers = np.array([ m.get_center_vertices() for m in self.meshes ])
		return np.mean(centers, axis=0)

	def save(self,filepath):
		with open(filepath+'.pkl', mode='wb') as f:
			pickle.dump( self, f)
	def load(self,filepath):
		try:
			with open(filepath+'.pkl', mode='rb') as f:
				return pickle.load( f )
		except FileNotFoundError as e:
			print(e)
		return None

