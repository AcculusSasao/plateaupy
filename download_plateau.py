import urllib.request, os, sys, subprocess, shutil, glob
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
		]
	},
	# add more dataset..
]
dbnames = [db['name'] for db in datasets]

parser = argparse.ArgumentParser(description='PLATEAU data downloader')
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
	elif fname[1] == '.png' or fname[1] == '.xml':
		cmd='cp {} {}'.format(url,dstpath)
	else:
		print('unknown ext',fname[1])
		return False
	print('  '+cmd)
	subprocess.run(cmd,shell=True)
	return True

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
	_tmpdir = '.tmp'

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
