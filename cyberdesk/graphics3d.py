from OpenGL.GL import *
import numpy as np
import cairo
from PIL import Image
from cyberdesk.math import line_intersection, distance
from functools import lru_cache, cached_property

ATTRIBUTE_LOCATION_POSITIONS = 0
ATTRIBUTE_LOCATION_TEXTUREUV = 1

class Texture:
	def __init__(self, size, data=None,
		format=GL_BGRA, type=GL_UNSIGNED_INT_8_8_8_8_REV, internal_format=GL_RGB,
		wrap_s=GL_REPEAT, wrap_t=GL_REPEAT,
		min_filter=GL_LINEAR, mag_filter=GL_LINEAR
	):
		self.size = size
		self.format = format
		self.type = type
		self.internal_format = internal_format
		self.size_initialized = False
		
		self.texture = glGenTextures(1)
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_s)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_t)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
		
		glBindTexture(GL_TEXTURE_2D, 0)
		
		if data is not None:
			self.update(data)
	
	def update(self, data):
		glBindTexture(GL_TEXTURE_2D, self.texture)
		
		if self.size_initialized:
			glTexSubImage2D(
				GL_TEXTURE_2D, # target
				0, # level
				0, # xoffset
				0, # yoffset
				*self.size, # width, height
				self.format, # format
				self.type, # type
				data # data
			)
		else:
			glTexImage2D(
				GL_TEXTURE_2D, # target
				0, # level
				self.internal_format,# internal format
				*self.size, # width, height
				0, # border
				self.format, # format
				self.type, # type
				data # data
			)
			self.size_initialized = True
		
		glBindTexture(GL_TEXTURE_2D, 0)
	
	def draw(self, corners, uvs=[(0, 0), (0, 1), (1, 1), (1, 0)]):
		draw_texture(self.texture, corners, uvs=uvs)
	
	def __del__(self):
		try:
			glDeleteTextures([self.texture])
		except:
			pass

class SubShader:
	def __init__(self, shader_type, code):
		self.shader = glCreateShader(shader_type)
		glShaderSource(self.shader, code)
		
		glCompileShader(self.shader)
		if glGetShaderiv(self.shader, GL_COMPILE_STATUS) != GL_TRUE:
			error = glGetShaderInfoLog(self.shader)
			glDeleteShader(self.shader)
			self.shader = None
			raise Exception("shader compile error: " + str(error))
	
	def __del__(self):
		if self.shader != None:
			glDeleteShader(self.shader)

class Shader:
	def __init__(self, vertex_shader_code, fragment_shader_code):
		self.program = glCreateProgram()
		self.vertex_shader = SubShader(GL_VERTEX_SHADER, vertex_shader_code)
		self.fragment_shader = SubShader(GL_FRAGMENT_SHADER, fragment_shader_code)
		
		glAttachShader(self.program, self.vertex_shader.shader)
		glAttachShader(self.program, self.fragment_shader.shader)
		glLinkProgram(self.program)
		
		if glGetProgramiv(self.program, GL_LINK_STATUS) != GL_TRUE:
			error = glGetProgramInfoLog(self.program)
			glDeleteProgram(self.program)
			self.program = None
			raise Exception("program link error: " + str(error))
	
	def uniform_location(self, name):
		return glGetUniformLocation(self.program, name)
	
	def attrib_location(self, name):
		return glGetAttribLocation(self.program, name)
	
	def __enter__(self):
		glUseProgram(self.program)
	
	def __exit__(self, type, value, traceback):
		glUseProgram(0)
	
	def __del__(self):
		if self.program != None:
			glDeleteProgram(self.program)

class OrtographicCamera:
	def __init__(self, l, r, b, t, n, f, background_color=(0, 0, 0, 1)):
		self.l = l
		self.r = r
		self.b = b
		self.t = t
		self.n = n
		self.f = f
		
		self.background_color = background_color
	
	@cached_property
	def matrix(self):
		return np.array([
			[2/(self.r-self.l), 0, 0, 0],
			[0, 2/(self.t-self.b), 0, 0],
			[0, 0, 2/(self.n-self.f), 0],
			[(self.l+self.r)/(self.l-self.r), (self.b+self.t)/(self.b-self.t), (self.n+self.f)/(self.n-self.f), 1],
		], dtype=np.float32)
	
	def clear_frame(self, framebuffer_rect):
		glViewport(*framebuffer_rect)
		
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_BLEND)
		
		glClearColor(*self.background_color)
		glClearDepth(1.0)
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LEQUAL)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	def render(self, geometry, material):
		with material:
			with geometry:
				glUniformMatrix4fv(material.shader.uniform_location("projection"), 1, GL_FALSE, self.matrix)
				geometry.draw()

class Material:
	def __init__(self, shader=None, color=(1, 1, 1, 1), texture=None):
		if shader == None:
			shader = default_shader()
		
		self.shader = shader
		self.color = color
		self.textures = {}
		
		if texture is not None:
			self.textures["main_texture"] = texture
	
	@property
	def texture(self):
		return self.textures["main_texture"]
	
	def __enter__(self):
		self.shader.__enter__()
		
		glUniform4f(self.shader.uniform_location("color"), *self.color)
		
		for index, (name, texture) in enumerate(self.textures.items()):
			glUniform1i(self.shader.uniform_location(name), index)
			glActiveTexture(GL_TEXTURE0 + index)
			glBindTexture(GL_TEXTURE_2D, texture.texture)
	
	def __exit__(self, type, value, traceback):
		for index in range(len(self.textures)):
			glActiveTexture(GL_TEXTURE0 + index)
			glBindTexture(GL_TEXTURE_2D, 0)
		
		self.shader.__exit__(type, value, traceback)

class Geometry:
	def __init__(self, positions, texcoords, indices, texcoords_size=2):
		self.positions = positions
		self.texcoords = texcoords
		self.indices = indices
		
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)
		
		self.position_buffer, self.texcoord_buffer, self.index_buffer = glGenBuffers(3)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.position_buffer)
		glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)
		glEnableVertexAttribArray(ATTRIBUTE_LOCATION_POSITIONS)
		glVertexAttribPointer(ATTRIBUTE_LOCATION_POSITIONS, 2, GL_FLOAT, GL_FALSE, 0, None)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.texcoord_buffer)
		glBufferData(GL_ARRAY_BUFFER, texcoords, GL_STATIC_DRAW)
		glEnableVertexAttribArray(ATTRIBUTE_LOCATION_TEXTUREUV)
		glVertexAttribPointer(ATTRIBUTE_LOCATION_TEXTUREUV, texcoords_size, GL_FLOAT, GL_FALSE, 0, None)
		
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)
		
		glBindVertexArray(0)
		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def update(self, positions=False, texcoords=False, indices=False):
		if positions:
			glBindBuffer(GL_ARRAY_BUFFER, self.position_buffer)
			glBufferSubData(GL_ARRAY_BUFFER, 0, self.positions)
			glBindBuffer(GL_ARRAY_BUFFER, 0)
		
		if texcoords:
			glBindBuffer(GL_ARRAY_BUFFER, self.texcoord_buffer)
			glBufferSubData(GL_ARRAY_BUFFER, 0, self.texcoords)
			glBindBuffer(GL_ARRAY_BUFFER, 0)
		
		if indices:
			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
			glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, self.indices)
			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def draw(self):
		glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
	
	def __enter__(self):
		glBindVertexArray(self.vao)
	
	def __exit__(self, type, value, traceback):
		glBindVertexArray(0)

default_vertex_shader_code = """
#version 410
layout(location = 0) in vec4 position;
layout(location = 1) in vec2 texcoord;
uniform mat4 projection;
uniform mat4 matrix;
out vec2 uv;

void main()
{
	gl_Position = projection * matrix * position;
	uv = texcoord;
}
"""

default_fragment_shader_code = """
#version 410
in vec2 uv;
uniform vec4 color;
uniform sampler2D main_texture;
out vec4 fragColor;

void main() {
	fragColor = texture(main_texture, uv) * color;
}
"""

@lru_cache(maxsize=None)
def default_shader():
	return Shader(default_vertex_shader_code, default_fragment_shader_code)

@lru_cache(maxsize=None)
def rect_geometry():
	positions = np.array([
		0, 0,
		1, 0,
		1, 1,
		0, 1,
	], dtype=np.float32)

	texcoords = np.array([
		0, 0,
		1, 0,
		1, 1,
		0, 1,
	], dtype=np.float32)
	
	indices = np.array([
		0, 3, 1, # top left, bottom left, top right
		1, 3, 2, # top right, bottom left, bottom right
	], dtype=np.uint32)
	
	return Geometry(positions, texcoords, indices)

# based on https://www.reedbeta.com/blog/quadrilateral-interpolation-part-1/
class QuadGeometry(Geometry):
	def __init__(self, corners=[[0, 0], [0, 0], [0, 0], [0, 0]], uvs=[[0, 0], [1, 0], [1, 1], [0, 1]]):
		self.corners = corners
		self.uvs = uvs
		
		self.calculate_buffers()
		
		self.indices = np.array([
			0, 3, 1, # top left, bottom left, top right
			1, 3, 2, # top right, bottom left, bottom right
		], dtype=np.uint32)
		
		super().__init__(self.positions, self.texcoords, self.indices, texcoords_size=3)
	
	def calculate_buffers(self):
		corners = np.array(self.corners)
		uvs = self.uvs
		
		center = line_intersection(corners[0], corners[2], corners[3], corners[1])
		if center is None:
			self.positions = np.zeros((6, 2), dtype=np.float32)
			self.texcoords = np.zeros((6, 3), dtype=np.float32)
			return
		
		distances = [distance(c, center) for c in corners]
		
		q = [
			(distances[0] + distances[2]) / distances[2],
			(distances[1] + distances[3]) / distances[3],
			(distances[2] + distances[0]) / distances[0],
			(distances[3] + distances[1]) / distances[1],
		]
		
		self.positions = np.array(corners, dtype=np.float32)
		
		self.texcoords = np.array([
			uvs[0][0]*q[0], uvs[0][1]*q[0], q[0],
			uvs[1][0]*q[1], uvs[1][1]*q[1], q[1],
			uvs[2][0]*q[2], uvs[2][1]*q[2], q[2],
			uvs[3][0]*q[3], uvs[3][1]*q[3], q[3],
		], dtype=np.float32)
	
	def update_corners(self, corners, uvs=None):
		self.corners = corners
		if uvs is not None:
			self.uvs = uvs
		
		self.calculate_buffers()
		self.update(positions=True, texcoords=True)

quad_vertex_shader_code = """
#version 410
layout(location = 0) in vec4 position;
layout(location = 1) in vec3 texcoord;
uniform mat4 projection;
out vec3 uvq;

void main()
{
	gl_Position = projection * position;
	uvq = texcoord;
}
"""

quad_fragment_shader_code = """
#version 410
in vec3 uvq;
uniform vec4 color;
uniform sampler2D main_texture;
out vec4 fragColor;

void main() {
	fragColor = texture(main_texture, uvq.xy / uvq.z) * color;
}
"""

@lru_cache(maxsize=None)
def quad_shader():
	return Shader(quad_vertex_shader_code, quad_fragment_shader_code)

class CanvasTexture:
	def __init__(self, size):
		self.size = size
		self.texture = Texture(size)
		self.data = np.zeros(shape=size, dtype=np.uint32)
		self.surface = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_ARGB32, *size)
		self.ctx = cairo.Context(self.surface)
	
	def update(self):
		self.texture.update(self.data)
	
	def draw(self, corners):
		self.update()
		self.texture.draw(corners)

def load_texture(filename, format=GL_RGB, type=GL_UNSIGNED_BYTE, internal_format=GL_RGB, **kwargs):
	image = Image.open(filename)
	data = np.array(list(image.getdata()), dtype=np.uint8)
	return Texture(image.size, data, format=format, type=type, internal_format=internal_format, **kwargs)

def corners_to_uvs(corners, size):
	return [
		(corners[0][0] / size[0], corners[0][1] / size[1]),
		(corners[1][0] / size[0], corners[1][1] / size[1]),
		(corners[2][0] / size[0], corners[2][1] / size[1]),
		(corners[3][0] / size[0], corners[3][1] / size[1]),
	]

@lru_cache(maxsize=None)
def default_texture():
	return Texture((1, 1), np.array([0xFF, 0xFF, 0xFF, 0xFF], dtype=np.uint8),
		format=GL_RGB, type=GL_UNSIGNED_BYTE, internal_format=GL_RGB)

def convert_color(color):
	if len(color) == 3:
		return (color[0]/256, color[1]/256, color[2]/256, 1)
	else:
		return color

@lru_cache
def color_quad_material(color):
	return Material(shader=quad_shader(), texture=default_texture(), color=convert_color(color))
