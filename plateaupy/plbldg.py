from plateaupy.plobj import plmesh, plobj
from plateaupy.plutils import *
from plateaupy.thirdparty.earcutpython.earcut.earcut import earcut
import numpy as np
import copy
import pickle
from lxml import etree

class Building:
	def __init__(self):
		self.id = None	# gml:id
		self.attr = dict()
		self.usage = None
		self.measuredHeight = None
		self.storeysAboveGround = None
		self.storeysBelowGround = None
		self.address = None
		self.buildingDetails = dict()
		self.extendedAttribute = dict()
		self.lod0RoofEdge = []
		self.lod1Solid = []
		#self.lod2Solid = []
		# lod2MultiSurface
		self.lod2ground = dict()
		self.lod2roof = dict()
		self.lod2wall = dict()
	def __str__(self):
		return 'Building id={}\n\
usage={}, measuredHeight={}, storeysAboveGround={}, storeysBelowGround={}\n\
address={}\n\
buildingDetails={}\n\
extendedAttribute={}\n\
attr={}'\
		.format(self.id, self.usage, self.measuredHeight, self.storeysAboveGround, self.storeysBelowGround, \
			self.address, self.buildingDetails, self.extendedAttribute, self.attr)

class appParameterizedTexture:
	def __init__(self):
		self.imageURI = ''
		self.targets = dict()

class plbldg(plobj):
	def __init__(self,filename=None):
		super().__init__()
		self.buildings = []	# list of Building
		if filename is not None:
			self.loadFile(filename)

	def loadFile(self,filename,dem=None):
		tree, root = super().loadFile(filename)
		# scan appearanceMember
		partex = []
		for app in tree.xpath('/core:CityModel/app:appearanceMember/app:Appearance/app:surfaceDataMember/app:ParameterizedTexture', namespaces=root.nsmap):
			par = appParameterizedTexture()
			for at in app.xpath('app:imageURI', namespaces=root.nsmap):
				par.imageURI = at.text
			for at in app.xpath('app:target', namespaces=root.nsmap):
				uri = at.attrib['uri']
				par.targets[uri] = np.array([str2floats(v).reshape((-1,2)) for v in at.xpath('app:TexCoordList/app:textureCoordinates', namespaces=root.nsmap)])
			#print(par.imageURI)
			partex.append(par)

		# scan cityObjectMember
		blds = tree.xpath('/core:CityModel/core:cityObjectMember/bldg:Building', namespaces=root.nsmap)
		for bld in blds:
			b = Building()
			# gml:id
			b.id = bld.attrib['{'+root.nsmap['gml']+'}id']
			# stringAttribute
			stringAttributes = bld.xpath('gen:stringAttribute', namespaces=root.nsmap)
			for at in stringAttributes:
				b.attr[at.attrib['name']] = at.getchildren()[0].text
			# genericAttributeSet
			genericAttributeSets = bld.xpath('gen:genericAttributeSet', namespaces=root.nsmap)
			for at in genericAttributeSets:
				vals = dict()
				for ch in at.getchildren():
					vals[ ch.attrib['name'] ] = ch.getchildren()[0].text
				b.attr[at.attrib['name']] = vals
			# usage
			for at in bld.xpath('bldg:usage', namespaces=root.nsmap):
				b.usage = at.text
			# measuredHeight
			for at in bld.xpath('bldg:measuredHeight', namespaces=root.nsmap):
				b.measuredHeight = at.text
			# storeysAboveGround
			for at in bld.xpath('bldg:storeysAboveGround', namespaces=root.nsmap):
				b.storeysAboveGround = at.text
			# storeysBelowGround
			for at in bld.xpath('bldg:storeysBelowGround', namespaces=root.nsmap):
				b.storeysBelowGround = at.text
			# address
			for at in bld.xpath('bldg:address/core:Address/core:xalAddress/xAL:AddressDetails/xAL:Address', namespaces=root.nsmap):
				b.address = at.text
			# buildingDetails
			for at in bld.xpath('uro:buildingDetails/uro:BuildingDetails', namespaces=root.nsmap):
				for ch in at.getchildren():
					tag = ch.tag
					tag = tag[ tag.rfind('}')+1: ]
					b.buildingDetails[tag] = ch.text
			# extendedAttribute
			for at in bld.xpath('uro:extendedAttribute/uro:KeyValuePair', namespaces=root.nsmap):
				ch = at.getchildren()
				b.extendedAttribute[ch[0].text] = ch[1].text
			# lod0RoofEdge
			vals = bld.xpath('bldg:lod0RoofEdge/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
			b.lod0RoofEdge = [str2floats(v).reshape((-1,3)) for v in vals]
			# lod1Solid
			vals = bld.xpath('bldg:lod1Solid/gml:Solid/gml:exterior/gml:CompositeSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList', namespaces=root.nsmap)
			b.lod1Solid = [str2floats(v).reshape((-1,3)) for v in vals]
			# lod2Solid
			#  nothing to do for parsing <bldg:lod2Solid>
			# lod2MultiSurface
			for bb in bld.xpath('bldg:boundedBy/bldg:GroundSurface/bldg:lod2MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing', namespaces=root.nsmap):
				polyid = bb.attrib['{'+root.nsmap['gml']+'}id']
				vals = bb.xpath('gml:posList', namespaces=root.nsmap)
				surf = [str2floats(v).reshape((-1,3)) for v in vals]
				b.lod2ground[polyid] = surf
			for bb in bld.xpath('bldg:boundedBy/bldg:RoofSurface/bldg:lod2MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing', namespaces=root.nsmap):
				polyid = bb.attrib['{'+root.nsmap['gml']+'}id']
				vals = bb.xpath('gml:posList', namespaces=root.nsmap)
				surf = [str2floats(v).reshape((-1,3)) for v in vals]
				b.lod2roof[polyid] = surf
			for bb in bld.xpath('bldg:boundedBy/bldg:WallSurface/bldg:lod2MultiSurface/gml:MultiSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing', namespaces=root.nsmap):
				polyid = bb.attrib['{'+root.nsmap['gml']+'}id']
				vals = bb.xpath('gml:posList', namespaces=root.nsmap)
				surf = [str2floats(v).reshape((-1,3)) for v in vals]
				b.lod2wall[polyid] = surf
			self.buildings.append(b)
		
		# vertices, triangles
		mesh = plmesh()
		for b in self.buildings:
			for plist in b.lod1Solid:
				vertices = [ convertPolarToCartsian( *x ) for x in plist ]
				res = earcut(np.array(vertices,dtype=np.int).flatten(), dim=3)
				if len(res) > 0:
					vstart = len(mesh.vertices)
					mesh.vertices.extend( vertices )
					mesh.triangles.extend( np.array(res).reshape((-1,3)) + vstart )
		self.meshes.append(mesh)

