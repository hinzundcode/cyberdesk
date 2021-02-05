from cyberdesk.paperspace import Paper
import cyberdesk.graphics2d
import cyberdesk.graphics3d
import cyberdesk.math
import cyberdesk.physics
import cyberdesk.input
from cyberdesk import Color

def get_environment():
	return {
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
		self.globals = None
		self.locals = None
	
	def show(self):
		with open(self.filename, "r") as file:
			source = file.read()
		
		self.code = compile(source, self.filename, "exec")
		
		self.globals = {
			**get_environment(),
			"shape": self.shape,
			"space": self.space,
		}
		self.locals = {}
		
		exec(self.code, self.globals, self.locals)
	
	def update(self):
		if "update" in self.locals:
			self.locals["update"]()
	
	def render(self):
		if "render" in self.locals:
			self.locals["render"]()
	
	def hide(self):
		if "hide" in self.locals:
			self.locals["hide"]()
		
		self.code = None
		self.globals = None
		self.locals = None
