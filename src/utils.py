import glfw
from OpenGL.GL import *
import os
import sys
import numpy as np
import cv2 as cv
import cv2.aruco as aruco
import platform

def maximize_current_window():
	system = platform.system()
	
	if system == "Darwin":
		os.system("""osascript -e 'tell application "System Events" to keystroke "f" using { command down, control down }'""")
	else:
		print("maximize_current_window() is not implemented for " + system + " yet")

def move_window_to_monitor(window, monitor_name, maximize=True):
	monitors = glfw.get_monitors()
	monitor = monitors[0]
	for m in monitors:
		if glfw.get_monitor_name(m) == monitor_name:
			monitor = m
	
	glfw.set_window_pos(window, *glfw.get_monitor_pos(monitor))
	if maximize:
		maximize_current_window()

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

def get_camera_capture(camera=1, width=1024, height=576):
	cap = cv.VideoCapture(camera)
	cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
	return cap

def get_camera_frame(cap, flip=-1):
	ret, frame = cap.read()
	frame = cv.flip(frame, flip)
	gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	return frame, gray

def detect_markers(gray):
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
	params = aruco.DetectorParameters_create()
	params.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
	corners, ids, rejectedImgPoints = aruco.detectMarkers(
		gray, aruco_dict, parameters=params)
	
	return corners, ids

def np_to_cv(m):
	width, height = m.shape
	return m.view("uint8").reshape((height, width, 4))

def cv_to_np(m):
	return m.view("uint32")

def load_calibration(file_name="calibration.npz"):
	if not os.path.exists(file_name):
		print('calibration data not found. run "python calibrate.py" first')
		sys.exit(1)
	
	return np.load(file_name)

def projection_main_loop(render, projection_size, monitor_name=None):
	if not glfw.init():
		return
	
	window = glfw.create_window(*projection_size, "Projection", None, None)
	if not window:
		glfw.terminate()
		return
	
	if monitor_name != None:
		move_window_to_monitor(window, monitor_name)

	glfw.make_context_current(window)
	
	set_orthagonal_camera(projection_size)
	
	projection_texture = create_texture(projection_size)
	
	cap = get_camera_capture()

	while not glfw.window_should_close(window):
		camera_frame, camera_frame_gray = get_camera_frame(cap)
		render(projection_texture, camera_frame)
		
		glfw.swap_buffers(window)
		glfw.poll_events()

	glfw.terminate()

def rect_corners(size, position=(0, 0)):
	x, y = position
	width, height = size
	
	return np.array([
		[x, y],
		[x+width, y],
		[x+width, y+height],
		[x, y+height]
	], dtype="float32")
