import numpy as np
import OpenGL.GL as GL
from cyberdesk.paperspace import Paper
import cyberdesk.graphics2d
import cyberdesk.graphics3d
import cyberdesk.math
import cyberdesk.physics
import cyberdesk.input
from cyberdesk import Color

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

class PythonPaper(Paper):
	def __init__(self, shape, filename):
		super().__init__(shape)
		self.filename = filename
		self.code = None
		self.scope = None
	
	def show(self):
		with open(self.filename, "r") as file:
			source = file.read()
		
		self.code = compile(source, self.filename, "exec")
		self.scope = {
			**get_environment(),
			"shape": self.shape,
			"space": self.space,
		}
		
		exec(self.code, self.scope, self.scope)
	
	def update(self):
		if "update" in self.scope:
			self.scope["update"]()
	
	def render(self):
		if "render" in self.scope:
			self.scope["render"]()
	
	def hide(self):
		if "hide" in self.scope:
			self.scope["hide"]()
		
		self.code = None
		self.scope = None
