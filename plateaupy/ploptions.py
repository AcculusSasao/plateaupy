class ploptions:
	def __init__(self) -> None:
		# show LOD2 texture
		self.bUseLOD2texture = False
		self.texturedir = 'cached'
		# use LOD0
		self.bUseLOD0 = False
		# force height = 0
		self.bHeightZero = False
		# divide the mesh 'AAAABB' automatically into the quarter, the group of 'AAAAABBCC'.
		#  specify (0,0)or(0,1)or(1,0)or(1,1)  as lat,lon
		#  Now, it is very hard-coded.  Do not use it.
		self.div6toQuarter = None
