import os
import numpy as np
from lxml import etree
import open3d as o3d
from plateaupy.plutils import *
import pickle

class plmesh:
	def __init__(self) -> None:
		self.vertices = []	# [ num_of_vertices,  3 ]  (float)
		self.triangles = []	# [ num_of_triangles, 3 ]  (int)
		self.texture_filename = None
		self.triangle_uvs = []			# [ 3 * num_of_triangles, 2 ]  (float)
		self.triangle_material_ids = []	# [ num_of_triangles ]  (int)
	
	def to_Open3D_TriangleMesh(self,color=None):
		mesh = o3d.geometry.TriangleMesh()
		mesh.vertices = o3d.utility.Vector3dVector( self.vertices )
		mesh.triangles = o3d.utility.Vector3iVector( self.triangles )
		if self.texture_filename is not None:
			mesh.textures = [o3d.io.read_image( self.texture_filename )]
			mesh.triangle_uvs = o3d.utility.Vector2dVector( self.triangle_uvs )
			mesh.triangle_material_ids = o3d.utility.IntVector( self.triangle_material_ids )
		elif color is not None:
			mesh.paint_uniform_color( color )
		mesh.compute_vertex_normals()
		return mesh

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

