import cv2 as cv
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
from ..gl import create_texture, update_texture, draw_texture, destroy_texture
from ..paperspace import Paper

class VideoPaper(Paper):
	def __init__(self, shape, video_size, video_file):
		super().__init__(shape)
		self.video_size = video_size
		self.video_file = video_file
		self.capture = None
		self.texture = None
	
	def show(self):
		self.capture = cv.VideoCapture(self.video_file)
		self.texture = create_texture(self.video_size)
	
	def update(self):
		if not self.shape.present:
			return
		
		ret, frame = self.capture.read()
		if not ret:
			self.capture.set(cv.CAP_PROP_POS_FRAMES, 0)
			ret, frame = self.capture.read()
			if not ret:
				return
		
		frame = cv.resize(frame, self.video_size)
		
		update_texture(self.texture, self.video_size, frame,
			format=GL_BGR, type=GL_UNSIGNED_BYTE)
	
	def render(self):
		draw_texture(self.texture, self.space.project_corners(self.shape.corners))
	
	def hide(self):
		self.capture.release()
		# TODO: destroy texture
