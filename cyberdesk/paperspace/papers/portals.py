import numpy as np
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
from cyberdesk.graphics3d import create_texture, update_texture, draw_texture, destroy_texture, draw_colored_rect
from cyberdesk.paperspace import Paper
from cyberdesk.math import scale_polygon

class PortalIn(Paper):
	def render(self):
		outer_rect = self.shape.corners
		inner_rect = scale_polygon(self.shape.corners, 0.9)
		draw_colored_rect(self.space.project_corners(outer_rect), (0, 137, 236))
		draw_colored_rect(self.space.project_corners(inner_rect), (0, 0, 0))

class PortalOut(Paper):
	def __init__(self, shape):
		super().__init__(shape)
		self.texture = None
		self.portal_in = None
	
	def show(self):
		self.texture = create_texture(self.space.camera_size)
	
	def update(self):
		portal_ins = self.space.get_papers_of_type(PortalIn)
		if portal_ins and portal_ins[0].visible:
			self.portal_in = portal_ins[0]
		else:
			self.portal_in = None
		
		update_texture(self.texture, self.space.camera_size,
			self.space.current_camera_frame, format=GL_BGR, type=GL_UNSIGNED_BYTE)
	
	def render(self):
		outer_rect = self.shape.corners
		draw_colored_rect(self.space.project_corners(outer_rect), (247, 127, 80))
		
		if self.portal_in != None:
			inner_rect = scale_polygon(self.shape.corners, 0.9)
			portal_in_inner_rect = np.array(scale_polygon(self.portal_in.shape.corners, 0.9))
			camera_size = np.array(self.space.camera_size)
			uvs = [
				portal_in_inner_rect[0] / camera_size,
				portal_in_inner_rect[3] / camera_size,
				portal_in_inner_rect[2] / camera_size,
				portal_in_inner_rect[1] / camera_size,
			]
			draw_texture(self.texture, self.space.project_corners(inner_rect), uvs)
	
	def hide(self):
		destroy_texture(self.texture)
		self.texture = None
