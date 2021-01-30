from plateaupy.plobj import plobj
from plateaupy.plutils import *
import numpy as np
import copy
from lxml import etree

class pldem(plobj):
	def __init__(self,filename=None):
		super().__init__()
		self.posLists = None	# list of 'posList'(LinearRing) : [*,4,3]
		if filename is not None:
			self.loadFile(filename)
		
	def loadFile(self,filename, num_search_coincident=100):
		tree, root = super().loadFile(filename)
		# posLists
		vals = tree.xpath('/core:CityModel/core:cityObjectMember/dem:ReliefFeature/dem:reliefComponent/dem:TINRelief/dem:tin/gml:TriangulatedSurface/gml:trianglePatches/gml:Triangle/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
		self.posLists = np.array([str2floats(v).reshape((-1,3)) for v in vals])
		#print(self.posLists.shape)
		# convert to XYZ
		posLists = copy.deepcopy(self.posLists)
		for x in posLists:
			for y in x:
				y[:] = convertPolarToCartsian(*y)
		# to vertices and triangles
		#   integrate vertices that are coincident.
		self.vertices = []
		self.triangles = np.zeros( (posLists.shape[0], 3), dtype=np.int )
		for xidx,x in enumerate(posLists):
			for yidx,y in enumerate(x[:3]):
				newid = -1
				num = xidx
				if num > num_search_coincident:
					num = num_search_coincident
				for _id, vvv in enumerate( self.vertices[xidx-num:] ):
					if vvv[0]==y[0] and vvv[1]==y[1] and vvv[2]==y[2]:
						newid = _id + xidx - num
						break
				if newid < 0:
					newid = len(self.vertices)
					self.vertices.append(y)
				self.triangles[xidx,yidx] = newid
	
	def save(self,filepath):
		np.savez_compressed(filepath, \
			location=self.location,lowerCorner=self.lowerCorner,upperCorner=self.upperCorner, \
			vertices=self.vertices,triangles=self.triangles, \
			posLists=self.posLists
			)
	def load(self,filepath):
		data = np.load( filepath + '.npz' )
		self.location = int(data['location'])
		self.lowerCorner = data['lowerCorner']
		self.upperCorner = data['upperCorner']
		self.vertices = data['vertices']
		self.triangles = data['triangles']
		self.posLists = data['posLists']
		return None
	
	'''
	def getPosListsTable(self):
		# create 2D table [lon,lat] to get height
		_posLists = self.posLists[:,:3].reshape( (-1,3) )
		tbl = dict()
		for p in _posLists:
			if _discrete(p[0]) in tbl:
				if _discrete(p[1]) in tbl[_discrete(p[0])]:
					pass
				else:
					tbl[_discrete(p[0])][_discrete(p[1])] = p[2]
			else:
				# new lon
				tbl[_discrete(p[0])] = dict()
				tbl[_discrete(p[0])][_discrete(p[1])] = p[2]
		return tbl
	'''
