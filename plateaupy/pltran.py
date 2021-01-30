from plateaupy import plobj
from plateaupy.plutils import *
from plateaupy.thirdparty.earcut-python.earcut import earcut
import numpy as np
import copy
from lxml import etree

class pltran(plobj):
	def __init__(self,filename=None,dem=None):
		super().__init__()
		self.posLists = None	# list of 'posList'(LinearRing)
		if filename is not None:
			self.loadFile(filename,dem)

	# triangulation for 2D points in gml:MultiSurface / gml:LinearRing
	#  use earcut-python
	#   (triangle lib  (ref: https://rufat.be/triangle/ ), scipy.spatial.Delaunay , cv2.Subdiv2D  are not proper.)

	def loadFile(self,filename,dem=None):
		tree, root = super().loadFile(filename)
		# posLists
		vals = tree.xpath('/core:CityModel/core:cityObjectMember/tran:Road/tran:lod1MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
		self.posLists = [str2floats(v).reshape((-1,3)) for v in vals]

		# convert function to get height using dem class
		'''
		if dem is None:
			tbl = None
			convfunc = convertByTblDummy
		else:
			tbl = dem.getPosListsTable()
			#print(tbl)
			convfunc = convertByTbl
		'''
		tbl = None
		convfunc = convertByTblDummy

		# vertices, triangles
		self.vertices = []
		self.triangles = []
		#self.posLists = self.posLists[:1000]
		# invoke multi processes
		for plist in self.posLists:
			vertices = [ convertPolarToCartsian( *convfunc(*x, tbl) ) for x in plist ]
			res = earcut.earcut(np.array(vertices, dtype=np.int).flatten(), dim=3)
			if len(res) > 0:
				triangles = np.array(res).reshape((-1,3)) + len(self.vertices)
				self.vertices.extend( vertices )
				self.triangles.extend( triangles )

	def save(self,filepath):
		np.savez_compressed(filepath, \
			location=self.location,lowerCorner=self.lowerCorner,upperCorner=self.upperCorner, \
			vertices=self.vertices,triangles=self.triangles, \
			posLists=self.posLists
			)
	def load(self,filepath):
		data = np.load( filepath + '.npz', allow_pickle=True )
		self.location = int(data['location'])
		self.lowerCorner = data['lowerCorner']
		self.upperCorner = data['upperCorner']
		self.vertices = data['vertices']
		self.triangles = data['triangles']
		self.posLists = data['posLists']
		### !!! TBD
		self.vertices[:,2] += temporary_road_height_offset
		return None
