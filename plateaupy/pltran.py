from plateaupy.plobj import plobj,plmesh
from plateaupy.plutils import *
from plateaupy.thirdparty.earcutpython.earcut.earcut import earcut
import numpy as np
import copy
from lxml import etree

# (!TBD!) road height [in meter] offset in loading, because the height values in .gml are always zero.
temporary_road_height_offset = 20

class pltran(plobj):
	def __init__(self,filename=None,dem=None):
		super().__init__()
		self.posLists = None	# list of 'posList'(LinearRing)
		if filename is not None:
			self.loadFile(filename,dem)

	def loadFile(self,filename,dem=None):
		tree, root = super().loadFile(filename)
		# posLists
		vals = tree.xpath('/core:CityModel/core:cityObjectMember/tran:Road/tran:lod1MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
		self.posLists = [str2floats(v).reshape((-1,3)) for v in vals]

		# vertices, triangles
		mesh = plmesh()
		#self.posLists = self.posLists[:1000]
		# invoke multi processes
		for plist in self.posLists:
			vertices = [ convertPolarToCartsian( *x ) for x in plist ]
			res = earcut(np.array(vertices, dtype=np.int).flatten(), dim=3)
			if len(res) > 0:
				triangles = np.array(res).reshape((-1,3)) + len(mesh.vertices)
				mesh.vertices.extend( vertices )
				mesh.triangles.extend( triangles )
		self.meshes.append(mesh)

	def load(self,filepath):
		res = super().load(filepath)
		### !!! TBD
		res.meshes[0].vertices = np.array(res.meshes[0].vertices)
		res.meshes[0].vertices[:,2] += temporary_road_height_offset
		return res
