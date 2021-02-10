import os
import sys
import numpy as np
import argparse
import open3d as o3d

import plateaupy

### usage
# python test/statistics.py -loc 533925 -c

# argparser
parser = argparse.ArgumentParser(description='plateaupy appviewer')
parser.add_argument('-paths','--paths',help='list of paths to CityGML dirctories',default=['../CityGML_01','../CityGML_02'],type=str,nargs='*')
parser.add_argument('-cmd','--cmd',help='special command [locations,codelists,dumpmeta]',default='',type=str)
parser.add_argument('-k','--kind',help='gml kind, -1:all, 0:bldg, 1:dem, 2:luse, 3:tran, 4:brid',default=-1,type=int)
parser.add_argument('-loc','--location',help='location index number',default=-1,type=int)
parser.add_argument('-c','--cache',action='store_true', help='use cache data')
parser.add_argument('-cpath','--cachepath',help='cache directory name',default='cached',type=str)
args = parser.parse_args()

# scan paths
pl = plateaupy.plparser(args.paths)

# load
pl.loadFiles( bLoadCache=args.cache, cachedir=args.cachepath, kind=args.kind, location=args.location, bUseLOD2texture=False )


# show Building_usage
print()
print('### Building_usage in ', args.location)
usage = pl.codelists['Building_usage']

res = dict()
for key in list(usage.keys()):
	res[key] = 0

for bldg in list(pl.bldg.values()):
	for bl in bldg.buildings:
		if bl.usage is not None:
			if bl.usage in res:
				res[bl.usage] += 1
			else:
				print('no key:', bl.usage )
total_cnt = 0
for key, cnt in list(res.items()):
	if cnt > 0:
		print('{} ({}) : {}'.format(key, usage[key], cnt))
	total_cnt += cnt
print('### total :', total_cnt)


# show extendedAttribute_key3
print()
print('### extendedAttribute_key3 建物用途コード（都道府県） in ', args.location)
ExtendedAttribute_key3 = pl.codelists['ExtendedAttribute_key3']
res = dict()
key = '3'
for bldg in list(pl.bldg.values()):
	for bl in bldg.buildings:
		if key in bl.extendedAttribute:
			val = bl.extendedAttribute[key]
			if val not in res:
				res[val] = 0
			res[val] += 1
res = sorted(res.items(), key=lambda x:int(x[0]))
total_cnt = 0
for key, cnt in res:
	if cnt > 0:
		if key in ExtendedAttribute_key3:
			print('{} ({}) : {}'.format(key, ExtendedAttribute_key3[key], cnt))
		else:
			print('{} ({}) : {}'.format(key, key, cnt))
	total_cnt += cnt
print('### total :', total_cnt)


# show storeysAboveGround, storeysBelowGround
print()
print('### storeysAboveGround, storeysBelowGround in ', args.location)
storeysAboveGround = dict()
storeysBelowGround = dict()
for bldg in list(pl.bldg.values()):
	for bl in bldg.buildings:
		if bl.storeysAboveGround is not None:
			if bl.storeysAboveGround not in storeysAboveGround:
				storeysAboveGround[bl.storeysAboveGround] = 0
			storeysAboveGround[bl.storeysAboveGround] += 1
		if bl.storeysBelowGround is not None:
			if bl.storeysBelowGround not in storeysBelowGround:
				storeysBelowGround[bl.storeysBelowGround] = 0
			storeysBelowGround[bl.storeysBelowGround] += 1
storeysAboveGround = sorted(storeysAboveGround.items(), key=lambda x:int(x[0]))
storeysBelowGround = sorted(storeysBelowGround.items(), key=lambda x:int(x[0]))
print('storeysAboveGround : ', storeysAboveGround)
print('storeysBelowGround : ', storeysBelowGround)
