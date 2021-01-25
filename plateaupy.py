import os
import sys
import copy
import numpy as np
import glob
import pickle
from lxml import etree
import open3d as o3d
#import multiprocessing
#import importlib
#from scipy.spatial import Delaunay
#import cv2
#import triangle# as tr

# local modules
import earcut
import compressed_pickle
from plutils import printMethods, str2floats, convertPolarToCartsian

# (!TBD!) road height [in meter] offset in loading, because the height values in .gml are always zero.
temporary_road_height_offset = 20

#def _discrete(x):
#	_c = 1000
#	return int(x * _c)

def convertByTbl( lon, lat, hei, tbl ):
	if _discrete(lon) in tbl:
		if _discrete(lat) in tbl[_discrete(lon)]:
			#print(tbl[_discrete(lon)][_discrete(lat)])
			return lon,lat,tbl[_discrete(lon)][_discrete(lat)]
	#print('no data', lon, ', ', lat)
	return lon,lat,hei

def convertByTblDummy( lon, lat, hei, tbl ):
	return lon,lat,hei

class plparser:
	def __init__(self, paths=None):
		# filenames
		self.filenames_bldg = []
		self.filenames_dem  = []
		self.filenames_luse = []
		self.filenames_tran = []
		# objects  (dictonary, the key is obj.location)
		self.bldg = dict()
		self.dem  = dict()
		self.luse = dict()
		self.tran = dict()
		# list of location numbers
		self.locations = []
		# add paths
		for path in paths:
			self.addPath(path)

	def addPath(self,path):	# path to CityGML
		print('search ' + path)
		# now, static path
		path_bldg = path + '/13100/udx/bldg'
		path_dem  = path + '/13100/udx/dem'
		path_luse = path + '/13100/udx/luse'
		path_tran = path + '/13100/udx/tran'
		val = sorted(glob.glob(path_bldg+'/*.gml'))
		print('  bldg : ',len(val), 'files')
		self.filenames_bldg.extend( val )
		val = sorted(glob.glob(path_dem+'/*.gml'))
		print('  dem  : ',len(val), 'files')
		self.filenames_dem.extend( val )
		val = sorted(glob.glob(path_luse+'/*.gml'))
		print('  luse : ',len(val), 'files')
		self.filenames_luse.extend( val )
		val = sorted(glob.glob(path_tran+'/*.gml'))
		print('  tran : ',len(val), 'files')
		self.filenames_tran.extend( val )
		# add locations
		locations = list(self.locations)
		locations.extend( [plobj.getLocationFromFilename( filename, True ) for filename in self.filenames_bldg] )
		locations.extend( [plobj.getLocationFromFilename( filename, True ) for filename in self.filenames_dem] )
		locations.extend( [plobj.getLocationFromFilename( filename, True ) for filename in self.filenames_luse] )
		locations.extend( [plobj.getLocationFromFilename( filename, True ) for filename in self.filenames_tran] )
		self.locations = sorted(list(set(locations)))

	'''
	@param bLoadCache:	load cache data or not
	@param cachedir: 	cache directory name
	@param kind:		specify the type of gml, plobj.ALL, plobj.BLDG,..
	@param location:	specify which gml data in the type are loaded, -1:all, <1000:array index, >=1000:location
	'''
	def loadFiles(self, bLoadCache=False, cachedir='cached', kind=None, location=-1):
		if kind is None:
			kind = plobj.ALL
		if cachedir is not None:
			os.makedirs( cachedir, exist_ok=True )
		# prepare filenames
		filenames_bldg = []
		filenames_dem  = []
		filenames_luse = []
		filenames_tran = []
		if kind==plobj.BLDG or kind==plobj.ALL:
			if location < 0:
				filenames_bldg = self.filenames_bldg
			elif location < 1000:
				filenames_bldg.append( self.filenames_bldg[location] )
			else:
				for filename in self.filenames_bldg:
					if plobj.getLocationFromFilename(filename,False) == location or plobj.getLocationFromFilename(filename,True) == location:
						filenames_bldg.append(filename)
		if kind==plobj.DEM or kind==plobj.ALL:
			if location < 0:
				filenames_dem  = self.filenames_dem
			elif location < 1000:
				filenames_dem.append( self.filenames_dem[location] )
			else:
				for filename in self.filenames_dem:
					if plobj.getLocationFromFilename(filename) == location:
						filenames_dem.append(filename)
		if kind==plobj.LUSE or kind==plobj.ALL:
			if location < 0:
				filenames_luse = self.filenames_luse
			elif location < 1000:
				filenames_luse.append( self.filenames_luse[location] )
			else:
				for filename in self.filenames_luse:
					if plobj.getLocationFromFilename(filename) == location:
						filenames_luse.append(filename)
		if kind==plobj.TRAN or kind==plobj.ALL:
			if location < 0:
				filenames_tran = self.filenames_tran
			elif location < 1000:
				filenames_tran.append( self.filenames_tran[location] )
			else:
				for filename in self.filenames_tran:
					if plobj.getLocationFromFilename(filename) == location:
						filenames_tran.append(filename)
		# load files
		if bLoadCache:
			print('### loading cache data..')
			print('# bldg')
			for f in filenames_bldg:
				obj = plbldg()
				res = obj.load(plobj.getCacheFilename(cachedir,f))
				if res is not None:
					obj = res
				self.bldg[obj.location] = obj
			print('# dem')
			for f in filenames_dem:
				obj = pldem()
				obj.load(plobj.getCacheFilename(cachedir,f))
				self.dem[obj.location] = obj
			print('# luse')
			for f in filenames_luse:
				obj = plluse()
				obj.load(plobj.getCacheFilename(cachedir,f))
				self.luse[obj.location] = obj
			print('# tran')
			for f in filenames_tran:
				obj = pltran()
				obj.load(plobj.getCacheFilename(cachedir,f))
				self.tran[obj.location] = obj
		else:
			print('### loading GML data..')
			print('# bldg')
			for f in filenames_bldg:
				obj = plbldg(f)
				self.bldg[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# dem')
			for f in filenames_dem:
				obj = pldem(f)
				self.dem[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# luse')
			for f in filenames_luse:
				obj = plluse(f)
				self.luse[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# tran')
			for f in filenames_tran:
				#obj = pltran(f, self.dem[ plobj.getLocationFromFilename(f) ])
				obj = pltran(f)
				self.tran[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))

	def getMeshes(self, color=None):
		meshes = []
		if False:
			# 1 by 1
			for obj in self.bldg.values():
				meshes.extend( obj.getMeshes(color=color) )
		else:
			# integration by location
			for location in self.locations:
				objs = []
				for key,value in self.bldg.items():
					if int(key//100)==location:
						objs.append(value)
				meshes.extend( plobj.getIntegratedMesh( objs, color=color ) )
		for obj in self.dem.values():
			meshes.extend( obj.getMeshes(color=color) )
		for obj in self.luse.values():
			meshes.extend( obj.getMeshes(color=color) )
		for obj in self.tran.values():
			meshes.extend( obj.getMeshes(color=color) )
		return meshes

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
		self.lod2Solid = []
	def __str__(self):
		return 'Building id={}\n\
usage={}, measuredHeight={}, storeysAboveGround={}, storeysBelowGround={}\n\
address={}\n\
buildingDetails={}\n\
extendedAttribute={}\n\
attr={}'\
		.format(self.id, self.usage, self.measuredHeight, self.storeysAboveGround, self.storeysBelowGround, \
			self.address, self.buildingDetails, self.extendedAttribute, self.attr)

class plbldg(plobj):
	def __init__(self,filename=None):
		super().__init__()
		self.buildings = []	# list of Building
		if filename is not None:
			self.loadFile(filename)

	def loadFile(self,filename,dem=None):
		tree, root = super().loadFile(filename)
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

			#print(b)
			self.buildings.append(b)
		# vertices, triangles
		self.vertices = []
		self.triangles = []
		for b in self.buildings:
			for plist in b.lod1Solid:
				vertices = [ convertPolarToCartsian( *x ) for x in plist ]
				res = earcut.earcut(np.array(vertices,dtype=np.int).flatten(), dim=3)
				if len(res) > 0:
					vstart = len(self.vertices)
					self.vertices.extend( vertices )
					self.triangles.extend( np.array(res).reshape((-1,3)) + vstart )

	def save(self,filepath):
		#compressed_pickle.save( filepath + '.pkl.bz2', self )
		with open(filepath+'.pkl', mode='wb') as f:
			pickle.dump( self, f)
	def load(self,filepath):
		#return compressed_pickle.load( filepath + '.pkl.bz2')	# compressed_pickle is too slow.
		with open(filepath+'.pkl', mode='rb') as f:
			return pickle.load( f )
		return None

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

# dummy
class plluse(plobj):
	def __init__(self,filename=None):
		super().__init__()
		if filename is not None:
			self.loadFile(filename)
	def loadFile(self,filename):
		pass
	def save(self,filepath):
		pass
	def load(self,filepath):
		return None

# test main
if __name__ == '__main__':
	#print(convertPolarToCartsian(36.103774791666666, 140.08785504166664, 40.12))
	#sys.exit()

	bLoadCache = True
	parser = plparser(['../CityGML_01','../CityGML_02'])
	parser.loadFiles(kind=plobj.BLDG,location=0,bLoadCache=False)
	parser.loadFiles(kind=plobj.BLDG,location=0,bLoadCache=True)

	window_name = 'dem'
	width = 640
	height = 480
	bgcolor = [1,1,1]
	vis = o3d.visualization.VisualizerWithKeyCallback()
	vis.create_window(window_name=window_name, width=width, height=height)
	vis.get_render_option().background_color = np.asarray(bgcolor)
	meshes = parser.getMeshes()
	for mesh in meshes:
		vis.add_geometry(mesh)

	#tetras = np.array( [[0,1,2,3]], dtype=np.int64 )

	print('run start')
	vis.run()
	vis.poll_events()
	vis.update_renderer()
