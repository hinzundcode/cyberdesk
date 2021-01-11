from OpenGL.GL import *

def set_orthagonal_camera(size):
	glViewport(0, 0, *size)
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0.0, size[0], 0, size[1], 0.0, 1.0)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def draw_texture(texture, corners):
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	glDisable(GL_LIGHTING)
	glEnable(GL_TEXTURE_2D)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glClearColor(0, 0, 0, 1.0)

	glBindTexture(GL_TEXTURE_2D, texture)
	
	glBegin(GL_QUADS)
	glTexCoord2f(0, 0)
	glVertex2f(*corners[3])
	glTexCoord2f(0, 1)
	glVertex2f(*corners[0])
	glTexCoord2f(1, 1)
	glVertex2f(*corners[1])
	glTexCoord2f(1, 0)
	glVertex2f(*corners[2])
	
	glEnd() # Mark the end of drawing

def create_texture(size, data=None):
	texture = glGenTextures(1)
	glPixelStorei(GL_UNPACK_ALIGNMENT,1)
	glBindTexture(GL_TEXTURE_2D, texture)
	
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	if data is not None:
		update_current_texture(size, data)
	
	glBindTexture(GL_TEXTURE_2D, 0)
	
	return texture

def update_texture(texture, size, data):
	glBindTexture(GL_TEXTURE_2D, texture)
	update_current_texture(size, data)
	glBindTexture(GL_TEXTURE_2D, 0)

def update_current_texture(size, data):
	glTexImage2D(
		GL_TEXTURE_2D, # target
		0, # level
		GL_RGB,# internal format
		*size, # width, height
		0, # border
		GL_BGRA, # format
		GL_UNSIGNED_INT_8_8_8_8_REV, # type
		data # data
	)
