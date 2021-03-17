import numpy as np
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
from cyberdesk.graphics3d import Texture, corners_to_uvs, QuadGeometry, quad_shader, Texture, Material, color_quad_material
from cyberdesk.paperspace import Paper
from cyberdesk.math import scale_polygon

PORTAL_IN_COLOR = (0, 137/256, 236/256, 1)
PORTAL_OUT_COLOR = (247/256, 127/256, 80/256, 1)

class PortalIn(Paper):
	def __init__(self, shape):
		super().__init__(shape)
		self.outer_geometry = None
		self.inner_geometry = None
	
	def show(self):
		self.outer_geometry = QuadGeometry()
		self.inner_geometry = QuadGeometry()
	
	def render(self):
		self.outer_geometry.update_corners(self.space.project_corners(self.shape.corners))
		self.inner_geometry.update_corners(self.space.project_corners(scale_polygon(self.shape.corners, 0.9)))
		self.space.camera.render(self.outer_geometry, color_quad_material(PORTAL_IN_COLOR))
		self.space.camera.render(self.inner_geometry, color_quad_material((0, 0, 0, 1)))
	
	def hide(self):
		self.outer_geometry = None
		self.inner_geometry = None

class PortalOut(Paper):
	def __init__(self, shape):
		super().__init__(shape)
		self.outer_geometry = None
		self.inner_geometry = None
		self.material = None
		self.portal_in = None
	
	def show(self):
		self.outer_geometry = QuadGeometry()
		self.inner_geometry = QuadGeometry()
		
		texture = Texture(self.space.camera_size, format=GL_BGR, type=GL_UNSIGNED_BYTE)
		self.material = Material(shader=quad_shader(), texture=texture)
	
	def update(self):
		portal_ins = self.space.get_papers_of_type(PortalIn)
		if portal_ins and portal_ins[0].visible:
			self.portal_in = portal_ins[0]
		else:
			self.portal_in = None
		
		self.material.texture.update(self.space.current_camera_frame)
	
	def render(self):
		self.outer_geometry.update_corners(self.space.project_corners(self.shape.corners))
		self.space.camera.render(self.outer_geometry, color_quad_material(PORTAL_OUT_COLOR))
		
		if self.portal_in != None:
			inner_rect = scale_polygon(self.shape.corners, 0.9)
			portal_in_inner_rect = scale_polygon(self.portal_in.shape.corners, 0.9)
			uvs = corners_to_uvs(portal_in_inner_rect, self.material.texture.size)
			self.inner_geometry.update_corners(self.space.project_corners(inner_rect), uvs)
			self.space.camera.render(self.inner_geometry, self.material)
	
	def hide(self):
		self.outer_geometry = None
		self.inner_geometry = None
		self.material = None
		self.portal_in = None
