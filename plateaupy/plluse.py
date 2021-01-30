from plateaupy import plobj
from plateaupy.plutils import *
import numpy as np
import copy
from lxml import etree

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
