import open3d as o3d
import numpy as np
import time
import cv2
usleep = lambda x: time.sleep(x/1000000.0)

class Visualizer3D:
	_bKeyPushedValue = -1
	_GLFW_KEY_ESCAPE	= 256
	_GLFW_KEY_SPACE		= 32
	_GLFW_KEY_TAB		= 258
	vislist = []

	def __init__(self, window_name='PLATEAU',width=800,height=600,bgcolor=[1,1,1], camparfile=None, z_far=None):
		vis = o3d.visualization.VisualizerWithKeyCallback()
		vis.create_window(window_name=window_name, width=width, height=height)
		vis.get_render_option().background_color = np.asarray(bgcolor)
		vis.get_render_option().mesh_show_back_face = True
		#vis.get_render_option().mesh_show_wireframe = True
		vis.get_render_option().show_coordinate_frame = True
		if z_far is not None:
			vis.get_view_control().set_constant_z_far(z_far)
		if camparfile is not None:
			campar = o3d.io.read_pinhole_camera_parameters( camparfile )
			vis.get_view_control().convert_from_pinhole_camera_parameters( campar )
		else:
			campar = None

		_bKeyPushedValue = -1
		# add key callbacks
		def keycallback_esc(vis):
			Visualizer3D._bKeyPushedValue = 27
		def keycallback_space(vis):
			Visualizer3D._bKeyPushedValue = 32
		def keycallback_tab(vis):
			Visualizer3D._bKeyPushedValue = 9
		vis.register_key_callback( self._GLFW_KEY_ESCAPE, keycallback_esc )
		vis.register_key_callback( self._GLFW_KEY_SPACE,  keycallback_space )
		vis.register_key_callback( self._GLFW_KEY_TAB,    keycallback_tab )

		self.recordfile = None
		self.writer = None
		
		self.vis = vis
		self.campar = campar
		self.vislist.append( self )
		self.clear()

	def destroy(self):
		self.stop_recording()
		self.vis.destroy_window()
	def clear(self, coord=0, bUpdateReset=True):
		self.vis.clear_geometries()
	def run(self):
		self.vis.run()
	def update(self):
		self.vis.poll_events()
		self.vis.update_renderer()
		self.record()
	
	def start_recording(self, filename, fps=30):
		self.recordfile = filename + '.avi'
		self.writer = None
		self.recfps = fps
	def stop_recording(self):
		self.recordfile = None
		if self.writer is not None:
			self.writer.release()
			self.writer = None
	def record(self):
		doOpen = False
		if self.recordfile is not None and self.writer is None:
			doOpen = True
		if self.writer is not None or doOpen:
			oimg = self.vis.capture_screen_float_buffer( do_render=False )
			img = np.array(oimg)
			img = np.array(img*255,dtype=np.uint8)
			img = img[:,:,[2,1,0]]
			if doOpen:
				fourcc = cv2.VideoWriter_fourcc(*'H264')
				self.writer = cv2.VideoWriter( self.recordfile, fourcc, self.recfps, (img.shape[1],img.shape[0]) )
			self.writer.write(img)

	@classmethod
	def wait(cls,usec=0):
		if usec == 0:
			usec = -1
		td = 10000  # 10msec
		waitusec = 0
		key = 0
		while usec != 0:
			for vis in cls.vislist:
				vis.update()
			if cls._bKeyPushedValue >= 0:
				key = cls._bKeyPushedValue
				cls._bKeyPushedValue = -1
			# wait
			if usec >= 0:
				waitusec = min( usec, td )
			else:
				waitusec = td
			usleep( waitusec )
			if usec >= 0:
				usec -= waitusec
		return key


### usage
if __name__ == '__main__':
	from plateaupy.plutils import createOpen3Dbox
	viwer = Visualizer3D()
	viwer.vis.add_geometry( createOpen3Dbox(bLineSet=False) )
	while True:
		key = viwer.wait(1)
		if key==27:	# ESC
			break
