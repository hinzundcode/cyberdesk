import glfw
import os
import platform
import cv2 as cv
from datetime import datetime
import time
from cyberdesk.graphics3d import set_orthagonal_camera, clear_frame
from cyberdesk.vision import get_camera_capture, get_camera_frame

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

def save_screenshot(frame):
	now = datetime.now()
	filename = "screenshot-{}.jpg".format(now.strftime("%Y%m%d-%H%M%S"))
	cv.imwrite(filename, frame)
	print("took a screenshot! "+filename)

def projection_main_loop(setup, render,
	projection_size=(1280, 720), camera_size=(1280, 720),
	monitor_name=None, maximize_window=True, camera_id=0):
	if not glfw.init():
		return
	
	if os.path.exists("gamecontrollerdb.txt"):
		with open("gamecontrollerdb.txt", "r") as file:
			gamecontrollerdb = file.read()
			glfw.update_gamepad_mappings(gamecontrollerdb)
	
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
	frame_count = 0
	fps_timer = time.time()+1

	took_screenshot = False
	while not glfw.window_should_close(window):
		try:
			# wait until window is open and maximized
			if window_ready == None or time.time() > window_ready:
				camera_frame, camera_frame_gray = get_camera_frame(cap)
				
				now = time.time()
				delta_time = now - frame_before if frame_before != None else 0
				frame_before = now
				
				frame_count += 1
				if now > fps_timer:
					print("fps:", frame_count)
					frame_count = 0
					fps_timer = now+1
				
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
