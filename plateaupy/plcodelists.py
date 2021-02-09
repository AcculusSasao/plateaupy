import os
import numpy as np
import glob
from lxml import etree
from plateaupy.plutils import *

def scan_codelists( dir_codelists ):
	gmlDict = dict()
	for filename in glob.glob( dir_codelists + '/*.xml' ):
		tree = etree.parse(filename)
		root = tree.getroot()
		# gml:name
		vals = tree.xpath('/gml:Dictionary/gml:name', namespaces=root.nsmap)
		if len(vals) > 0:
			titlename = vals[0].text
			gmlDict[titlename] = dict()
			defs = tree.xpath('/gml:Dictionary/gml:dictionaryEntry/gml:Definition', namespaces=root.nsmap)
			# pair of description and name
			for deff in defs:
				description = deff.xpath('gml:description', namespaces=root.nsmap)[0].text
				name        = deff.xpath('gml:name', namespaces=root.nsmap)[0].text
				gmlDict[titlename][name] = description
	return gmlDict
