from OpenGL.GL import *

def set_orthagonal_camera(size):
	glViewport(0, 0, *size)
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	#glOrtho(0.0, size[0], 0, size[1], 0.0, 1.0)
	glOrtho(0.0, size[0], size[1], 0, 0.0, 1.0) # flipped
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def clear_frame():
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	glDisable(GL_LIGHTING)
	glEnable(GL_TEXTURE_2D)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glClearColor(0, 0, 0, 1.0)

def draw_texture(texture, corners):
	glBindTexture(GL_TEXTURE_2D, texture)
	
	# corner order: bottom_left, top_left, top_right, bottom_right
	# (0, 0) is normally bottom left on the screen,
	# but the orthagonal camera is flipped
	glBegin(GL_QUADS)
	glTexCoord2f(0, 0)
	glVertex2f(*corners[0]) # tl
	glTexCoord2f(0, 1)
	glVertex2f(*corners[3]) # bl
	glTexCoord2f(1, 1)
	glVertex2f(*corners[2]) # br
	glTexCoord2f(1, 0)
	glVertex2f(*corners[1]) # tr
	glEnd() # Mark the end of drawing
	
	glBindTexture(GL_TEXTURE_2D, 0)

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

def update_texture(texture, size, data, format=GL_BGRA, type=GL_UNSIGNED_INT_8_8_8_8_REV):
	glBindTexture(GL_TEXTURE_2D, texture)
	update_current_texture(size, data, format=format, type=type)
	glBindTexture(GL_TEXTURE_2D, 0)

def update_current_texture(size, data, format=GL_BGRA, type=GL_UNSIGNED_INT_8_8_8_8_REV):
	glTexImage2D(
		GL_TEXTURE_2D, # target
		0, # level
		GL_RGB,# internal format
		*size, # width, height
		0, # border
		format, # format
		type, # type
		data # data
	)
