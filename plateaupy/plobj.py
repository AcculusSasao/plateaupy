import os
import numpy as np
from lxml import etree
import open3d as o3d
from plateaupy.plutils import *

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
		self.location = 0	# location number
		self.lowerCorner = np.zeros((3))	# lowerCorner (lon,lat,height)
		self.upperCorner = np.zeros((3))	# upperCorner
		self.vertices = None	# list of vertices  : [*,3] 
		self.triangles = None	# list of triangles : [*,3] (int)

	def loadFile(self,filename):
		print('load', filename)
		self.location = self.getLocationFromFilename(filename)
		#print(self.location)
		tree = etree.parse(filename)
		root = tree.getroot()
		#print(root.tag)
		#print(root.attrib)
		# lowerCorner, upperCorner
		vals = tree.xpath('/core:CityModel/gml:boundedBy/gml:Envelope/gml:lowerCorner', namespaces=root.nsmap)
		if len(vals) > 0:
			self.lowerCorner = str2floats(vals[0])
		vals = tree.xpath('/core:CityModel/gml:boundedBy/gml:Envelope/gml:upperCorner', namespaces=root.nsmap)
		if len(vals) > 0:
			self.upperCorner = str2floats(vals[0])
		return tree, root

	def getMeshes(self,color=None,vertices=None,triangles=None,div=10000000):
		if vertices is None:
			vertices = self.vertices
		if triangles is None:
			triangles = self.triangles
			if triangles is None:
				return []
		num = len(triangles)
		meshes = []
		for idx0 in range(0,num,div):
			mesh = o3d.geometry.TriangleMesh()
			mesh.vertices = o3d.utility.Vector3dVector( vertices )

			idx1 = idx0 + div
			if idx1 > num:
				idx1 = num
			mesh.triangles = o3d.utility.Vector3iVector( triangles[idx0:idx1] )
			_color = color
			if _color is None:
				_color = np.random.rand(3)
			mesh.paint_uniform_color( _color )
			mesh.compute_triangle_normals()
			mesh.compute_vertex_normals()
			meshes.append(mesh)
		return meshes

	@classmethod
	def getIntegratedMesh(cls,objs,color=None):
		vertices  = []
		triangles = []
		for obj in objs:
			triangles.extend( list(np.array(obj.triangles,dtype=np.int) + len(vertices)) )
			vertices.extend( obj.vertices )

		mesh = o3d.geometry.TriangleMesh()
		mesh.vertices = o3d.utility.Vector3dVector( vertices )
		mesh.triangles = o3d.utility.Vector3iVector( triangles )
		_color = color
		if _color is None:
			_color = np.random.rand(3)
		mesh.paint_uniform_color( _color )
		mesh.compute_triangle_normals()
		mesh.compute_vertex_normals()
		return [mesh]
