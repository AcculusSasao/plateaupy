import urllib.request, os, sys, subprocess, shutil, glob
from distutils.dir_util import copy_tree
import argparse

datasets = [
	{	'name':	'plateau-tokyo23ku-citygml-2020',
		'url' : 'https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020',
		'codelists': [
			'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/codelists_2.zip',
		],
		'metadata': [
			'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/udx131002020_2.zip',
			'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/13000_metadata_lsld_2.xml',
			'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/13000_metadata_fld_2.xml',
		],
		'citygml_base': 'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/',
		'citygml': [
			'533925_2.zip',
			'533926_2.7z',
			'533934_2.zip',
			'533935_2.7z',
			'533936_3.7z',
			'533937_2.zip',
			'533944_2.zip',
			'533945_2.7z',
			'533946_2.7z',
			'533947_2.zip',
			'533954_2.zip',
			'533955_2.zip',
			'533956_2.zip',
			'533957_2.zip',
		],
		'citygml_ex': [
			'doshasaigai_LOD1_2.zip',
			'kouzuisinsuisoutei_2.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/a48396a3-b76f-4e7d-bc7b-04f354e3e5e9/resource/1015f435-3108-45b2-be42-08f78639d37b/download/tokyo23ku-all.png',
			'https://www.geospatial.jp/ckan/dataset/a48396a3-b76f-4e7d-bc7b-04f354e3e5e9/resource/40f54174-7c7d-4f9f-b392-8c8ad585b09b/download/tokyo23ku-1.png',
			'https://www.geospatial.jp/ckan/dataset/a48396a3-b76f-4e7d-bc7b-04f354e3e5e9/resource/40803cc8-c45c-4a81-bb8b-43ea83e3c04b/download/tokyo23ku-2.png',
			'https://www.geospatial.jp/ckan/dataset/a48396a3-b76f-4e7d-bc7b-04f354e3e5e9/resource/780b8865-6642-4537-a6b3-884d259eb591/download/tokyo23ku-3.png',
			'https://www.geospatial.jp/ckan/dataset/a48396a3-b76f-4e7d-bc7b-04f354e3e5e9/resource/0ad3e254-0c51-4346-ac9b-204e1077f7a0/download/tokyo23ku-4.png',
			'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/tokyo23ku/tokyo23ku-ps_2.zip',
		],
	},
	{	'name':	'plateau-27100-osaka-shi-2020',
		'url' : 'https://www.geospatial.jp/ckan/dataset/plateau-27100-osaka-shi-2020',
		'citygml_all': [
			#'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/27100_osaka-shi_citygml_2.zip',
			'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/27100_osaka-shi_citygml3.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/45719509-717d-4866-a191-cb9e07cbe2a0/resource/1352e404-237b-4d8e-b6cc-5866be50ad13/download/27100osaka-shicatalog.xlsx',
		],
	},
	{
		'name':	'plateau-14100-yokohama-city-2020',
		'url' :	'https://www.geospatial.jp/ckan/dataset/plateau-14100-yokohama-city-2020',
		'citygml_all': [
			#'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14100_yokohama-shi_citygml_2.zip',
			'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14100_yokohama-shi_citygml3.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/6e445bad-43ab-4a89-ac4d-6dcdbd769608/resource/8c947eff-e4f6-4e8e-a6b7-d4765ce1ca26/download/14100yokohama-shicatalog.xlsx',
		],
	},
	{
		'name':	'plateau-14130-kawasaki-shi-2020',
		'url' :	'https://www.geospatial.jp/ckan/dataset/plateau-14130-kawasaki-shi-2020',
		'citygml_all': [
			#'https://gic-plateau.s3-ap-northeast-1.amazonaws.com/2020/14130_kawasaki-shi_CityGML.zip',
			'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14130_kawasaki-shi_CityGML2.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/b7d8c630-05ef-4fbd-84e7-96a132204e3f/resource/32cb50b4-0085-47b0-be16-9d122b6e245f/download/14130kawasaki-shicatalog.xlsx',
		],
	},
	{
		'name':	'plateau-14201-yokosuka-shi-2020',
		'url' :	'https://www.geospatial.jp/ckan/dataset/plateau-14201-yokosuka-shi-2020',
		'citygml_all': [
			#'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14201_yokosuka-shi_citygml.zip',
			'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14201_yokosuka-shi_citygml2.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/21e5d06c-442d-406c-be99-c376e80aee37/resource/4b75ee2a-8283-4680-af53-bfd6fbc4f434/download/14201-yokosuka-shicatalog.xlsx',
		],
	},
	{
		'name':	'plateau-14382-hakone-machi-2020',
		'url' :	'https://www.geospatial.jp/ckan/dataset/plateau-14382-hakone-machi-2020',
		'citygml_all': [
			#'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14382_hakone-machi_CityGML_3.zip',
			'https://gic-plateau.s3.ap-northeast-1.amazonaws.com/2020/14382_hakone-machi_CityGML4.zip',
		],
		'specs': [
			'https://www.geospatial.jp/ckan/dataset/32410073-80ac-4cb0-849c-bad92e83ef69/resource/f5b37e14-8ba8-44f1-b32c-8f97ea640203/download/14382hakone-machicatalog.xlsx',
		],
	},
	# add more dataset..
]
'''
	{
		'name':	'',
		'url' :	'',
		'citygml_all': [
			'',
		],
		'specs': [
			'',
		],
	},
'''
dbnames = [db['name'] for db in datasets]

parser = argparse.ArgumentParser(description='Download & extract PLATEAU dataset')
parser.add_argument('db',type=str,help='-1(all) or specify dataset, as str or index in '+str(dbnames))
parser.add_argument('--basedir',type=str,default='CityGML2020',help='dst base directory')
parser.add_argument('--no_download',action='store_true',help='not download files.')
parser.add_argument('--no_extract',action='store_true',help='not extract files.')

args = parser.parse_args()

dbs = []
if args.db=='-1':
	dbs = datasets
elif args.db in dbnames:
	dbs = [datasets[ dbnames.index(args.db) ]]
elif args.db.isdecimal() and 0 <= int(args.db) and int(args.db) < len(datasets):
	dbs = [datasets[int(args.db)]]
else:
	print('No dataset:',args.db)
	sys.exit(-1)

def download(url,dstpath):
	os.makedirs(dstpath,exist_ok=True)
	filename = os.path.basename(url)
	print('  download',url,'to',dstpath)
	urllib.request.urlretrieve(url,dstpath+'/'+filename)

def extract(url,dstpath):
	os.makedirs(dstpath,exist_ok=True)
	fname = os.path.splitext(os.path.basename(url))
	if fname[1] == '.zip':
		cmd='unzip -o -q {} -d {}'.format(url,dstpath)
	elif fname[1] == '.7z':
		cmd='7z x -y -o{} {} > /dev/null'.format(dstpath,url)
	elif fname[1] == '.png' or fname[1] == '.xml' or fname[1] == '.xlsx' or fname[1] == '.xls':
		cmd='cp {} {}'.format(url,dstpath)
	else:
		print('unknown ext',fname[1])
		return False
	print('  '+cmd)
	subprocess.run(cmd,shell=True)
	return True
def copy_files(url,dstpath):
	cmd='cp -a {} {}'.format(url,dstpath)
	print('  '+cmd)
	subprocess.run(cmd,shell=True)
def copy_tree_(url,dstpath):
	copy_tree(url,dstpath)
	print('  copy_tree {} {}'.format(url,dstpath))

basedir = args.basedir
ardir = 'archive'
for db in dbs:
	print(db['name'])
	_basedir = basedir+'/'+db['name']
	_ardir = _basedir+'/'+ardir+'/'
	_codelistdir = _basedir+'/codelists/'
	_metadatadir = _basedir+'/metadata/'
	_specdir = _basedir+'/specification/'
	_udxdir = _basedir+'/udx/'
	_alldir = _basedir
	_tmpdir = _basedir+'/.tmp'

	if not args.no_download:
		if 'specs' in db:
			for xx in db['specs']:
				download(xx,_ardir)
		if 'codelists' in db:
			for xx in db['codelists']:
				download(xx,_ardir)
		if 'metadata' in db:
			for xx in db['metadata']:
				download(xx,_ardir)
		if 'citygml' in db:
			for xx in db['citygml']:
				download(db['citygml_base']+xx,_ardir)
		if 'citygml_all' in db:
			for xx in db['citygml_all']:
				download(xx,_ardir)
	if not args.no_extract:
		if 'specs' in db:
			for xx in db['specs']:
				extract(_ardir+os.path.basename(xx),_specdir)
		if 'codelists' in db:
			for xx in db['codelists']:
				extract(_ardir+os.path.basename(xx),_codelistdir)
		if 'metadata' in db:
			for xx in db['metadata']:
				extract(_ardir+os.path.basename(xx),_metadatadir)
		if 'citygml' in db:
			for xx in db['citygml']:
				if os.path.exists(_tmpdir):
					shutil.rmtree(_tmpdir)
				extract(_ardir+os.path.basename(xx),_tmpdir)
				for yy in glob.glob(_tmpdir+'/*'):
					pname = os.path.splitext(os.path.basename(yy))[0]
					extract(yy,_udxdir+pname)
			shutil.rmtree(_tmpdir)
		if 'citygml_all' in db:
			for xx in db['citygml_all']:
				if os.path.exists(_tmpdir):
					shutil.rmtree(_tmpdir)
				extract(_ardir+os.path.basename(xx),_tmpdir)
				tmpfiles = glob.glob(_tmpdir+'/*')
				if 'udx' in tmpfiles:
					copy_tree_( _tmpdir, _alldir )
					#for yy in tmpfiles:
					#	copy_files( yy, _alldir )
				elif len(tmpfiles)>0 and os.path.exists(tmpfiles[0]+'/udx'):
					copy_tree_( tmpfiles[0], _alldir )
					#for yy in glob.glob(tmpfiles[0]+'/*'):
					#	copy_files( yy, _alldir )
				else:
					bFound = False
					for yy in tmpfiles:
						if os.path.splitext(yy)[1] == '.zip' or os.path.splitext(yy)[1] == '.7z':
							extract(yy, _tmpdir)
					for tt in ['codelists','metadata','specification','udx']:
						for zz in glob.glob(_tmpdir+'/**/'+tt,recursive=True):
							copy_tree_(zz,_alldir+'/'+tt)
							bFound = True
					if not bFound:
						for tt in ['bldg','tran','luse','urf','dem','fld','tnm','lsld','brid','frn']:
							for zz in glob.glob(_tmpdir+'/**/'+tt,recursive=True):
								copy_files(zz,_udxdir)
								bFound = True
					if not bFound:
						print('\nerror! unknown dir structure:', tmpfiles)
				for yy in glob.glob(_udxdir+'**/*.zip',recursive=True):
					extract(yy, os.path.dirname(yy))
				for yy in glob.glob(_udxdir+'**/*.7z',recursive=True):
					extract(yy, os.path.dirname(yy))
			shutil.rmtree(_tmpdir)
