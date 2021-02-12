from plateaupy.plobj import plobj,plmesh
from plateaupy.plutils import *
from plateaupy.ploptions import ploptions
from plateaupy.thirdparty.earcutpython.earcut.earcut import earcut
import numpy as np
import copy
import os
from lxml import etree

# (!TBD!) road height [in meter] offset in loading, because the height values in .gml are always zero.
#temporary_road_height_offset = 20

class pltran(plobj):
	def __init__(self,filename=None, options=ploptions(),dem=None):
		super().__init__()
		self.kindstr = 'tran'
		self.posLists = None	# list of 'posList'(LinearRing)
		if filename is not None:
			self.loadFile(filename, options=options, dem=dem)

	def loadFile(self,filename, options=ploptions(),dem=None):
		tree, root = super().loadFile(filename)
		lt,rb = convertMeshcodeToLatLon( os.path.basename(filename).split('_')[0] )
		#center = (np.array(lt)+np.array(rb))/2
		center = ( lt[0]*0.8+rb[0]*0.2, lt[1]*0.2+rb[1]*0.8 )
		# posLists
		vals = tree.xpath('/core:CityModel/core:cityObjectMember/tran:Road/tran:lod1MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
		self.posLists = [str2floats(v).reshape((-1,3)) for v in vals]
		if options.bHeightZero:
			for x in self.posLists:
				x[:,2] = 1	# to be a little bit more than 0
		# vertices, triangles
		mesh = plmesh()
		#self.posLists = self.posLists[:1000]
		# invoke multi processes
		usebit = []
		for plist in self.posLists:
			vertices = [ convertPolarToCartsian( *x ) for x in plist ]
			res = earcut(np.array(vertices, dtype=np.int).flatten(), dim=3)
			if len(res) > 0:
				triangles = np.array(res).reshape((-1,3)) + len(mesh.vertices)
				mesh.vertices.extend( vertices )
				mesh.triangles.extend( triangles )
				if options.div6toQuarter is not None:
					for x in plist:
						bit = True
						if options.div6toQuarter is not None:
							lat = x[0]
							lon = x[1]
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
						usebit.append(bit)
		# remove 
		if options.div6toQuarter is not None:
			newtriangles = []
			for tri in mesh.triangles:
				if usebit[tri[0]] and usebit[tri[1]] and usebit[tri[2]]:
					newtriangles.append( tri )
			mesh.triangles = np.array(newtriangles)
			
		self.meshes.append(mesh)

	def load(self,filepath):
		res = super().load(filepath)
		res.meshes[0].vertices = np.array(res.meshes[0].vertices)
		### !!! TBD
		#res.meshes[0].vertices[:,2] += temporary_road_height_offset
		return res
