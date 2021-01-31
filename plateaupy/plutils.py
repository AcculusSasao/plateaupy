import math
import numpy as np
import random
import string

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
def convertPolarToCartsian( lon, lat, hei ):
	cosLon = math.cos( lon * math.pi/180 )
	sinLon = math.sin( lon * math.pi/180 )
	cosLat = math.cos( lat * math.pi/180 )
	sinLat = math.sin( lat * math.pi/180 )
	# Semi-mejor axis  [in meter]
	a = 6378137
	# Flattening
	f = 1 / 298.257222101
	# Eccentricity
	e = math.sqrt( 2*f - f*f )
	W = math.sqrt( 1 - e*e * sinLat*sinLat )
	# Prime vertical radius of curvature
	N = a / W
	#
	h = hei
	X = ( N + h ) * cosLon * cosLat
	Y = ( N + h ) * cosLon * sinLat
	Z = ( N * (1 - e*e) + h ) * sinLon
	return np.array([X,Y,Z])
