import cv2 as cv
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
from cyberdesk.graphics3d import Texture
from cyberdesk.paperspace import Paper

class VideoPaper(Paper):
	def __init__(self, shape, video_size, video_file):
		super().__init__(shape)
		self.video_size = video_size
		self.video_file = video_file
		self.capture = None
		self.texture = None
	
	def show(self):
		self.capture = cv.VideoCapture(self.video_file)
		self.texture = Texture(self.video_size, format=GL_BGR, type=GL_UNSIGNED_BYTE)
	
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
		self.texture.update(frame)
	
	def render(self):
		tl, tr, br, bl = self.shape.corners
		corners = [bl, tl, tr, br] # landscape
		self.texture.draw(self.space.project_corners(corners))
	
	def hide(self):
		self.capture.release()
		self.capture = None
		self.texture = None
