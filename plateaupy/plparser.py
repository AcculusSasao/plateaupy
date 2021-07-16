import os
from plateaupy.ploptions import ploptions
import numpy as np
import glob
from lxml import etree
from plateaupy.plobj import plobj
from plateaupy.plbldg import plbldg
from plateaupy.pldem import pldem
from plateaupy.plluse import plluse
from plateaupy.pltran import pltran
from plateaupy.plutils import *
from plateaupy.plcodelists import scan_codelists

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
		path_bldg = path + '/udx/bldg'
		path_dem  = path + '/udx/dem'
		path_luse = path + '/udx/luse'
		path_tran = path + '/udx/tran'
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
		# parse codelists
		dir_codelists = glob.glob( path + '/codelists/' )
		if len(dir_codelists) > 0:
			self.codelists = scan_codelists(dir_codelists[0])

	'''
	@param bLoadCache:	load cache data or not
	@param cachedir: 	cache directory name
	@param kind:		specify the type of gml, plobj.ALL, plobj.BLDG,..
	@param location:	specify which gml data in the type are loaded, -1:all, <1000:array index, >=1000:location
	'''
	def loadFiles(self, bLoadCache=False, cachedir='cached', kind=None, location=-1, options=ploptions()):
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
				if (options.div6toQuarter is not None) and (options.div6toQuarter != plobj.get6QuarterFromFilename(f)):
					continue
				obj = plbldg()
				res = obj.load(plobj.getCacheFilename(cachedir,f))
				if res is not None:
					obj = res
				self.bldg[obj.location] = obj
			print('# dem')
			for f in filenames_dem:
				obj = pldem()
				res = obj.load(plobj.getCacheFilename(cachedir,f))
				if res is not None:
					obj = res
				self.dem[obj.location] = obj
			print('# luse')
			for f in filenames_luse:
				obj = plluse()
				res = obj.load(plobj.getCacheFilename(cachedir,f))
				if res is not None:
					obj = res
				self.luse[obj.location] = obj
			print('# tran')
			for f in filenames_tran:
				obj = pltran()
				res = obj.load(plobj.getCacheFilename(cachedir,f))
				if res is not None:
					obj = res
				self.tran[obj.location] = obj
		else:
			print('### loading GML data..')
			print('# bldg')
			for f in filenames_bldg:
				if (options.div6toQuarter is not None) and (options.div6toQuarter != plobj.get6QuarterFromFilename(f)):
					continue
				obj = plbldg(f, options=options)
				self.bldg[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# dem')
			for f in filenames_dem:
				obj = pldem(f, options=options)
				self.dem[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# luse')
			for f in filenames_luse:
				obj = plluse(f, options=options)
				self.luse[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))
			print('# tran')
			for f in filenames_tran:
				#obj = pltran(f, self.dem[ plobj.getLocationFromFilename(f) ])
				obj = pltran(f, options=options)
				self.tran[obj.location] = obj
				obj.save(plobj.getCacheFilename(cachedir,f))

	def get_Open3D_TriangleMesh(self, color=None, kindbits=255, wireonly=False):
		meshes = []
		if kindbits & (1 << plobj.BLDG):
			for obj in self.bldg.values():
				meshes.extend( obj.get_Open3D_TriangleMesh(color=color, wireonly=wireonly) )
		if kindbits & (1 << plobj.DEM):
			for obj in self.dem.values():
				meshes.extend( obj.get_Open3D_TriangleMesh(color=color, wireonly=wireonly) )
		if kindbits & (1 << plobj.LUSE):
			for obj in self.luse.values():
				meshes.extend( obj.get_Open3D_TriangleMesh(color=color, wireonly=wireonly) )
		if kindbits & (1 << plobj.TRAN):
			for obj in self.tran.values():
				meshes.extend( obj.get_Open3D_TriangleMesh(color=color, wireonly=wireonly) )
		return meshes
	
	def write_Open3D_ply_files(self, savepath, color=None):
		for obj in self.bldg.values():
			obj.write_Open3D_ply_files( savepath=savepath, color=color )
		for obj in self.dem.values():
			obj.write_Open3D_ply_files( savepath=savepath, color=color )
		for obj in self.luse.values():
			obj.write_Open3D_ply_files( savepath=savepath, color=color )
		for obj in self.tran.values():
			obj.write_Open3D_ply_files( savepath=savepath, color=color )

	def show_Blender_Objects(self, vbase=None):
		import bpy
		scene = bpy.context.scene
		for obj in self.bldg.values():
			_obj = obj.get_Blender_Objects(vbase=vbase)
			for _o in _obj:
				scene.collection.objects.link(_o)
		for obj in self.dem.values():
			_obj = obj.get_Blender_Objects(vbase=vbase)
			for _o in _obj:
				scene.collection.objects.link(_o)
		for obj in self.luse.values():
			_obj = obj.get_Blender_Objects(vbase=vbase)
			for _o in _obj:
				scene.collection.objects.link(_o)
		for obj in self.tran.values():
			_obj = obj.get_Blender_Objects(vbase=vbase)
			for _o in _obj:
				scene.collection.objects.link(_o)
		bpy.context.view_layer.update()
