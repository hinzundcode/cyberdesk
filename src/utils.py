import glfw
from .gl import *
from .graphics import *
from .physics import *
import os
import sys
import numpy as np
import cv2 as cv
import cv2.aruco as aruco
import platform
from datetime import datetime
import time

def maximize_current_window():
	system = platform.system()
	
	if system == "Darwin":
		os.system("""osascript -e 'tell application "System Events" to keystroke "f" using { command down, control down }'""")
	else:
		print("maximize_current_window() is not implemented for " + system + " yet")

def move_window_to_monitor(window, monitor_name):
	monitors = glfw.get_monitors()
	monitor = None
	for m in monitors:
		if glfw.get_monitor_name(m) == monitor_name:
			monitor = m
	
	if monitor is not None:
		glfw.set_window_pos(window, *glfw.get_monitor_pos(monitor))
		return True
	else:
		return False

def get_camera_capture(width, height, camera_id=0):
	cap = cv.VideoCapture(camera_id)
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

def main_loop_config_args(config):
	args = {}
	
	keys = [
		"projection_size", "camera_size",
		"monitor_name", "maximize_window",
		"camera_id",
	]
	
	for key in keys:
		if hasattr(config, key):
			args[key] = getattr(config, key)
	
	return args

def projection_main_loop(setup, render,
	projection_size=(1280, 720), camera_size=(1280, 720),
	monitor_name=None, maximize_window=True, camera_id=0):
	if not glfw.init():
		return
	
	window = glfw.create_window(*projection_size, "Projection", None, None)
	if not window:
		glfw.terminate()
		return
	
	def on_key(window, key, scancode, action, mods):
		if key in [glfw.KEY_Q, glfw.KEY_ESCAPE]:
			glfw.set_window_should_close(window, True)
	glfw.set_key_callback(window, on_key)
	
	window_ready = None
	
	if monitor_name != None:
		moved = move_window_to_monitor(window, monitor_name)
		if moved and maximize_window:
			maximize_current_window()
			window_ready = time.time() + 2

	glfw.make_context_current(window)
	
	set_orthagonal_camera(projection_size)
	
	state = setup()
	
	cap = get_camera_capture(*camera_size, camera_id=camera_id)
	
	start_time = time.time()
	frame_before = None

	took_screenshot = False
	while not glfw.window_should_close(window):
		try:
			# wait until window is open and maximized
			if window_ready == None or time.time() > window_ready:
				camera_frame, camera_frame_gray = get_camera_frame(cap)
				
				now = time.time()
				if frame_before != None:
					delta_time = now - frame_before
				else:
					delta_time = 0
				frame_before = now
				
				clear_frame()
				
				render(state,
					camera_frame=camera_frame,
					camera_frame_gray=camera_frame_gray,
					delta_time=delta_time)
			
			glfw.swap_buffers(window)
			glfw.poll_events()
			
			if glfw.get_key(window, glfw.KEY_S):
				if not took_screenshot:
					save_screenshot(camera_frame)
					took_screenshot = True
			else:
				took_screenshot = False
		except KeyboardInterrupt:
			glfw.set_window_should_close(window, True)
	
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

def centered_rect_corners(position, size):
	width = np.array([size[0], 0])
	height = np.array([0, size[1]])
	
	return np.array([
		position - width/2 - height/2,
		position + width/2 - height/2,
		position + width/2 + height/2,
		position - width/2 + height/2,
	], dtype="float32")

def normalize(vector):
	return vector / np.sqrt(np.sum(vector**2))

def save_screenshot(frame):
	now = datetime.now()
	filename = "screenshot-{}.jpg".format(now.strftime("%Y%m%d-%H%M%S"))
	cv.imwrite(filename, frame)
	print("took a screenshot! "+filename)

class Marker:
	def __init__(self, id):
		self.id = id
		self.corners = None
		self.absent_frames = None
	
	@property
	def present(self):
		return self.absent_frames == 0

class MarkerTracker:
	def __init__(self):
		self.markers = {}
	
	def process_frame(self, marker_corners, marker_ids):
		for _, marker in self.markers.items():
			if marker.absent_frames != None:
				marker.absent_frames += 1
		
		if marker_ids is not None:
			for i in range(len(marker_ids)):
				marker_id = str(marker_ids[i][0])
				corners = marker_corners[i][0]
				marker = self.get(marker_id)
				marker.corners = corners
				marker.absent_frames = 0
	
	def get(self, marker_id):
		marker_id = str(marker_id)
		
		if marker_id not in self.markers:
			self.markers[marker_id] = Marker(marker_id)
		
		return self.markers[marker_id]
