from OpenGL.GL import *
import glfw
import os
import platform
import cv2 as cv
from datetime import datetime
import time
from cyberdesk.graphics3d import OrtographicCamera
from cyberdesk.vision import get_camera_capture, get_camera_frame

def try_maximize_window_osx():
	try:
		from AppKit import NSApplication
	except ImportError:
		print("try_maximize_window_osx(): install pyobjc to maximize the window on osx")
		return True
	
	app = NSApplication.sharedApplication()
	
	# wait until window is ready
	if app.mainWindow() is not None:
		menu = app.mainMenu()
		window_menu = menu.itemArray()[1].submenu()
		
		for i, menu_item in enumerate(window_menu.itemArray()):
			if menu_item.action() == "toggleFullScreen:":
				window_menu.performActionForItemAtIndex_(i)
		
		return True
	
	return False

def try_maximize_window():
	system = platform.system()
	
	if system == "Darwin":
		return try_maximize_window_osx()
	else:
		print("try_maximize_window() is not implemented for " + system + " yet")
		return True

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

def main_loop_config_args(config, **kwargs):
	args = {}
	
	keys = [
		"projection_size", "camera_size",
		"monitor_name", "maximize_window",
		"camera_id",
	]
	
	for key in keys:
		if hasattr(config, key):
			args[key] = getattr(config, key)
	
	return { **args, **kwargs }

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
	
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3) # 3.2 or 4.1
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
	glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, 1)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
	
	#glfw.window_hint(glfw.RESIZABLE, False)
	
	window = glfw.create_window(*projection_size, "Projection", None, None)
	if not window:
		glfw.terminate()
		return
	
	def on_key(window, key, scancode, action, mods):
		if key in [glfw.KEY_Q, glfw.KEY_ESCAPE]:
			glfw.set_window_should_close(window, True)
	glfw.set_key_callback(window, on_key)
	
	wait_until_window_maximized = False
	
	if monitor_name != None:
		moved = move_window_to_monitor(window, monitor_name)
		if moved and maximize_window:
			wait_until_window_maximized = True

	glfw.make_context_current(window)
	
	print("Vendor:", glGetString(GL_VENDOR))
	print("OpenGL Version:", glGetString(GL_VERSION))
	print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION))
	print("Renderer:", glGetString(GL_RENDERER))

	camera = OrtographicCamera(0.0, *projection_size, 0, -1.0, 1.0)
	framebuffer_rect = (0, 0, *glfw.get_framebuffer_size(window))
	
	state = setup()
	
	cap = get_camera_capture(*camera_size, camera_id=camera_id)
	
	start_time = time.time()
	frame_before = None
	frame_count = 0
	fps_timer = time.time()+1

	took_screenshot = False
	while not glfw.window_should_close(window):
		if wait_until_window_maximized:
			if try_maximize_window():
				wait_until_window_maximized = False
		
		try:
			# wait until window is open and maximized
			if not wait_until_window_maximized:
				camera_frame, camera_frame_gray = get_camera_frame(cap)
				
				now = time.time()
				delta_time = now - frame_before if frame_before != None else 0
				frame_before = now
				
				frame_count += 1
				if now > fps_timer:
					print("fps:", frame_count)
					frame_count = 0
					fps_timer = now+1
				
				camera.clear_frame(framebuffer_rect)
				
				render(state,
					camera_frame=camera_frame,
					camera_frame_gray=camera_frame_gray,
					camera=camera,
					delta_time=delta_time,
					window=window)
			
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
