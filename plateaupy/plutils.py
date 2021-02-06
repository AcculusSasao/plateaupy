import math
import numpy as np
import random
import string
import copy
import cv2

def printMethods(obj):
	for x in dir(obj):
		print( x, ':', type(eval("obj."+x)) )

def randomname(n):
	randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
	return ''.join(randlst)

def str2floats(x):
	return np.array([float(i) for i in x.text.split(' ')])

# convert (longitude[rad],latitude[rad],height[meter]) into (X,Y,Z[meter])
#
# ref: https://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/transf.html
# ref: https://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/algorithm/trans/trans_alg.html
# ref: http://tancro.e-central.tv/grandmaster/excel/radius.html
def convertPolarToCartsian( lat, lon, hei ):
	cosLat = math.cos( lat * math.pi/180 )
	sinLat = math.sin( lat * math.pi/180 )
	cosLon = math.cos( lon * math.pi/180 )
	sinLon = math.sin( lon * math.pi/180 )
	# Semi-mejor axis  [in meter]
	a = 6378137
	# Flattening
	f = 1 / 298.257222101
	# Eccentricity
	e = math.sqrt( 2*f - f*f )
	W = math.sqrt( 1 - e*e * sinLon*sinLon )
	# Prime vertical radius of curvature
	N = a / W
	#
	h = hei
	X = ( N + h ) * cosLat * cosLon
	Y = ( N + h ) * cosLat * sinLon
	Z = ( N * (1 - e*e) + h ) * sinLat
	return np.array([X,Y,Z])

# return left-top (latitude,longitude) and right-bottom
def convertMeshcodeToLatLon( meshcode ):
	smeshcode = str(meshcode)
	length = len(smeshcode)
	lat = int(smeshcode[0:2]) * 2 / 3
	lon = int(smeshcode[2:4]) + 100
	lat2 = lat + 2/3
	lon2 = lon + 1
	if length > 4:
		if length >= 6:
			lat += int(smeshcode[4:5]) * 2 / 3 / 8
			lon += int(smeshcode[5:6]) / 8
			lat2 = lat + 2 / 3 / 8
			lon2 = lon + 1/8
		if length >= 8:
			lat += int(smeshcode[6:7]) * 2 / 3 / 8 / 10
			lon += int(smeshcode[7:8]) / 8 / 10
			lat2 = lat + 2 / 3 / 8 / 10
			lon2 = lon + 1 / 8 / 10
	return [lat2,lon],[lat,lon2]

class VerticesTransformer:
	def __init__(self, lowerCorner=None, upperCorner=None) -> None:
		self.rot = np.eye(3)		# rotation matrix 3x3
		self.trans = np.zeros((3))	# translation vector 3
		self.scaleX = 1				# scale value of x axis
		self.aspectXY = 1			# ratio of X / Y
		if lowerCorner is not None and upperCorner is not None:
			self.calc( lowerCorner, upperCorner )
		
	# calculate rot, trans, scaleX, aspectXY
	#  lowerCorner, upperCorner must be [lat, lon, 0]
	def calc(self, lowerCorner, upperCorner):
		# prepare 3D points correspoinding (0,0), (0,1), (1,0)
		lt = convertPolarToCartsian(*lowerCorner)
		rt = convertPolarToCartsian( lowerCorner[0], upperCorner[1], 0 )
		lb = convertPolarToCartsian( upperCorner[0], lowerCorner[1], 0 )
		# base point
		self.trans = copy.deepcopy(lt)
		# 2 vectors
		vecx = rt - self.trans
		vecy = lb - self.trans
		# aspect ratio X/Y
		self.aspectXY = np.linalg.norm(vecx) / np.linalg.norm(vecy)
		# scale X by vecx
		self.scaleX = 1 / np.linalg.norm(vecx)
		vecx *= self.scaleX
		vecy *= self.scaleX
		# rotation on Z axis
		angleZ = math.atan2( vecx[1], vecx[0] )
		rotZ = cv2.Rodrigues( np.array([0,0,-angleZ]) )[0].T
		# rotation on Y axis
		angleY = math.atan2( vecx[2], vecx[0]/math.cos(angleZ) )
		rotY = cv2.Rodrigues( np.array([0,-angleY,0]) )[0].T
		rot = rotZ.dot( rotY )
		# apply for vecy
		vecy = vecy.dot( rot )
		# rotation on X axis
		angleX = math.atan2( vecy[2], vecy[1] )
		rotX = cv2.Rodrigues( np.array([-angleX,0,0]) )[0].T
		rot = rot.dot( rotX )
		self.rot = rot

	def transform(self, v, normscale=1, normaspect=True ):
		vv = (v - self.trans).dot(self.rot)
		if normscale is not None:
			vv *= self.scaleX * normscale
		if normaspect:
			vv[:,1] *= self.aspectXY
		return vv

	def inv_transform(self, vv, normscale=1, normaspect=True ):
		invrot = np.linalg.inv(self.rot)
		v = copy.deepcopy(vv)
		if normaspect:
			v[:,1] /= self.aspectXY
		if normscale is not None:
			v /= (self.scaleX * normscale)
		return v.dot( invrot ) + self.trans


# create Open3D box 
#  translation (numpy.ndarray[float64[3, 1]]) – A 3D vector to transform the geometry
def createOpen3Dbox(size=1,translation=None, bLineSet=True, color=None):
	import open3d as o3d
	mesh = o3d.geometry.TriangleMesh.create_box(width=size,height=size,depth=size)
	if translation is not None:
		mesh.translate(translation,relative=False)
	if color is not None:
		mesh.paint_uniform_color( color )
	mesh.compute_vertex_normals()
	if bLineSet:
		mesh = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
	return mesh
