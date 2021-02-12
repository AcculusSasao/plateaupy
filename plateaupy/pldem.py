from plateaupy.plobj import plobj,plmesh
from plateaupy.plutils import *
from plateaupy.ploptions import ploptions
import numpy as np
import copy
import os
from lxml import etree

class pldem(plobj):
	def __init__(self,filename=None, options=ploptions()):
		super().__init__()
		self.kindstr = 'dem'
		self.posLists = None	# list of 'posList'(LinearRing) : [*,4,3]
		if filename is not None:
			self.loadFile(filename, options=options)
		
	def loadFile(self,filename, options=ploptions(), num_search_coincident=100):
		tree, root = super().loadFile(filename)
		lt,rb = convertMeshcodeToLatLon( os.path.basename(filename).split('_')[0] )
		center = (np.array(lt)+np.array(rb))/2
		# posLists
		vals = tree.xpath('/core:CityModel/core:cityObjectMember/dem:ReliefFeature/dem:reliefComponent/dem:TINRelief/dem:tin/gml:TriangulatedSurface/gml:trianglePatches/gml:Triangle/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
		self.posLists = np.array([str2floats(v).reshape((-1,3)) for v in vals])
		if options.bHeightZero:
			self.posLists[:,:,2] = 0
		#print(self.posLists.shape)
		# convert to XYZ
		posLists = copy.deepcopy(self.posLists)
		usebit = []
		for x in posLists:
			for yidx,y in enumerate(x):
				bit = True
				if options.div6toQuarter is not None:
					lat = y[0]
					lon = y[1]
					if lat < center[0]:
						lat = 0
					else:
						lat = 1
					if lon < center[1]:
						lon = 0
					else:
						lon = 1
					if (lat,lon) != options.div6toQuarter:
						bit = False
				if yidx < 3:
					usebit.append(bit)
				y[:] = convertPolarToCartsian(*y)
		# to vertices and triangles
		#   integrate vertices that are coincident.
		mesh = plmesh()
		mesh.triangles = np.zeros( (posLists.shape[0], 3), dtype=np.int )
		for xidx,x in enumerate(posLists):
			for yidx,y in enumerate(x[:3]):
				newid = -1
				if options.div6toQuarter is None:
					num = xidx
					if num > num_search_coincident:
						num = num_search_coincident
					for _id, vvv in enumerate( mesh.vertices[xidx-num:] ):
						if vvv[0]==y[0] and vvv[1]==y[1] and vvv[2]==y[2]:
							newid = _id + xidx - num
							break
				if newid < 0:
					newid = len(mesh.vertices)
					mesh.vertices.append(y)
				mesh.triangles[xidx,yidx] = newid
		# remove 
		if options.div6toQuarter is not None:
			newtriangles = []
			for tri in mesh.triangles:
				if usebit[tri[0]] and usebit[tri[1]] and usebit[tri[2]]:
					newtriangles.append( tri )
			mesh.triangles = np.array(newtriangles)
			
		self.meshes.append(mesh)


