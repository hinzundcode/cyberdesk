import numpy as np
import OpenGL.GL as GL
from cyberdesk.paperspace import Paper
from cyberdesk.graphics2d import draw_text_centered, draw_text_multiline
from cyberdesk.graphics3d import CanvasTexture, Material, QuadGeometry, quad_shader
import cyberdesk.graphics2d
import cyberdesk.graphics3d
import cyberdesk.math
import cyberdesk.physics
import cyberdesk.input
from cyberdesk import Color
import traceback

def get_environment():
	return {
		"np": np,
		"GL": GL,
		"graphics2d": cyberdesk.graphics2d,
		"graphics3d": cyberdesk.graphics3d,
		"math": cyberdesk.math,
		"physics": cyberdesk.physics,
		"input": cyberdesk.input,
		"Color": Color,
	}

def draw_exception(canvas, exception):
	ctx = canvas.ctx
	
	ctx.set_source_rgb(*Color.RED)
	ctx.rectangle(0, 0, *canvas.size)
	ctx.fill()
	
	ctx.set_source_rgb(*Color.WHITE)
	
	draw_text_centered(ctx, "Exception", (70, 15), (255, 40), font_size=30)
	
	text = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__, limit=-1))
	draw_text_multiline(ctx, text, (10, 100), font_size=20)

class PythonPaper(Paper):
	def __init__(self, shape, filename):
		super().__init__(shape)
		self.filename = filename
		self.code = None
		self.scope = None
		self.exception = None
		self.exception_canvas = CanvasTexture((400, 280))
		self.exception_material = Material(shader=quad_shader(), texture=self.exception_canvas.texture)
		self.exception_geometry = QuadGeometry()
		self.initialized = False
	
	def show(self):
		with open(self.filename, "r") as file:
			source = file.read()
		
		self.code = compile(source, self.filename, "exec")
		self.scope = {
			**get_environment(),
			"shape": self.shape,
			"space": self.space,
		}
		
		try:
			exec(self.code, self.scope, self.scope)
			self.initialized = True
		except Exception as e:
			self.exception = e
	
	def update(self):
		if self.initialized:
			self.exception = None
			
			if "update" in self.scope:
				try:
					self.scope["update"]()
				except Exception as e:
					self.exception = e
	
	def render(self):
		if self.initialized:
			if self.exception is None:
				if "render" in self.scope:
					try:
						self.scope["render"]()
					except Exception as e:
						self.exception = e
		
		if self.exception is not None:
			draw_exception(self.exception_canvas, self.exception)
			self.exception_canvas.update()
			self.exception_geometry.update_corners(self.space.project_corners(self.shape.corners))
			self.space.camera.render(self.exception_geometry, self.exception_material)
	
	def hide(self):
		if self.initialized:
			if "hide" in self.scope:
				try:
					self.scope["hide"]()
				except Exception as e:
					print(e)
		
		self.code = None
		self.scope = None
		self.initialized = False
