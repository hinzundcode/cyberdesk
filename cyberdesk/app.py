from OpenGL.GL import *
import glfw
import os
import platform
import cv2 as cv
from datetime import datetime
import time
from cyberdesk.graphics3d import OrtographicCamera, ortographic_camera_params
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

class Window:
	def __init__(self, setup, render, size, title="Window", monitor=None, maximize=True, resizable=False):
		self.setup = setup
		self.render = render
		self.size = size
		self.title = title
		self.monitor = monitor
		self.maximize = maximize
		self.resizable = resizable
		self.framebuffer_size = size
	
	def show(self):
		glfw.window_hint(glfw.RESIZABLE, self.resizable)
		
		self.window = glfw.create_window(*self.size, self.title, None, None)
		if not self.window:
			raise Exception("can't create window")
		
		glfw.set_key_callback(self.window, self.on_key)
		
		self.wait_until_window_maximized = False
		
		if self.monitor != None:
			moved = move_window_to_monitor(self.window, self.monitor)
			if moved and self.maximize:
				self.wait_until_window_maximized = True
		
		glfw.make_context_current(self.window)
		
		print("Vendor:", glGetString(GL_VENDOR))
		print("OpenGL Version:", glGetString(GL_VERSION))
		print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION))
		print("Renderer:", glGetString(GL_RENDERER))
		
		self.state = self.setup(window=self)
	
	def on_key(self, window, key, scancode, action, mods):
		if key in [glfw.KEY_Q, glfw.KEY_ESCAPE]:
			glfw.set_window_should_close(self.window, True)
	
	def update(self):
		if glfw.window_should_close(self.window):
			return False
		
		if self.wait_until_window_maximized:
			if try_maximize_window():
				self.wait_until_window_maximized = False
		
		try:
			# wait until window is open and maximized
			if not self.wait_until_window_maximized:
				self.framebuffer_size = glfw.get_framebuffer_size(self.window)
				self.render(self.state,
					window=self)
			
			glfw.swap_buffers(self.window)
			glfw.poll_events()
		except KeyboardInterrupt:
			glfw.set_window_should_close(self.window, True)
		
		return True

class CameraCapture:
	def __init__(self, camera_size, camera_id):
		self.camera_size = camera_size
		self.camera_id = camera_id
		self.capture = None
	
	def setup(self, fn):
		def decorator(**kwargs):
			self.capture = get_camera_capture(*self.camera_size, camera_id=self.camera_id)
			return fn(**kwargs)
		
		return decorator
	
	def render(self, fn):
		def decorator(state, **kwargs):
			camera_frame, camera_frame_gray = get_camera_frame(self.capture)
			return fn(state,
				camera_frame=camera_frame,
				camera_frame_gray=camera_frame_gray,
				**kwargs)
		
		return decorator
	
	def __del__(self):
		if self.capture != None:
			self.capture.release()

class Timer:
	def __init__(self):
		self.frame_before = None
	
	def setup(self, fn):
		return fn
	
	def render(self, fn):
		def decorator(state, **kwargs):
			frame_start = time.time()
			delta_time = frame_start - self.frame_before if self.frame_before != None else 0
			self.frame_before = frame_start
			
			return fn(state,
				frame_start=frame_start,
				delta_time=delta_time,
				**kwargs)
		
		return decorator

class FPSCounter:
	def __init__(self):
		self.frame_count = 0
		self.fps_timer = None
	
	def setup(self, fn):
		return fn
	
	def render(self, fn):
		def decorator(state, frame_start, **kwargs):
			if self.fps_timer == None:
				self.fps_timer = frame_start+1
			
			self.frame_count += 1
			if frame_start > self.fps_timer:
				print("fps:", self.frame_count)
				self.frame_count = 0
				self.fps_timer = frame_start+1
			
			return fn(state,
				frame_start=frame_start,
				**kwargs)
		
		return decorator

class WindowCamera:
	def setup(self, fn):
		def decorator(window, **kwargs):
			self.camera = OrtographicCamera(*ortographic_camera_params(window.framebuffer_size))
			return fn(window=window,
				camera=self.camera,
				**kwargs)
		
		return decorator
	
	def render(self, fn):
		def decorator(state, window, **kwargs):
			self.camera.update(*ortographic_camera_params(window.framebuffer_size))
			self.camera.clear_frame()
			
			return fn(state,
				window=window,
				camera=self.camera,
				**kwargs)
		
		return decorator

def main_loop(window):
	if not glfw.init():
		raise Exception("can't initialize glfw")
	
	if os.path.exists("gamecontrollerdb.txt"):
		with open("gamecontrollerdb.txt", "r") as file:
			gamecontrollerdb = file.read()
			glfw.update_gamepad_mappings(gamecontrollerdb)
	
	glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3) # 3.2 or 4.1
	glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
	glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, 1)
	glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
	glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, False)
	
	window.show()
	
	while window.update():
		pass
	
	glfw.terminate()

def setup_stack(stack):
	def decorator(fn):
		for component in reversed(stack):
			fn = component.setup(fn)
		return fn
	
	return decorator

def render_stack(stack):
	def decorator(fn):
		for component in reversed(stack):
			fn = component.render(fn)
		return fn
	
	return decorator

def projection_main_loop(setup, render,
	projection_size=(1280, 720), camera_size=(1280, 720),
	monitor_name=None, maximize_window=True, camera_id=0):
	
	capture = CameraCapture(camera_size, camera_id)
	timer = Timer()
	fps_counter = FPSCounter()
	camera = WindowCamera()
	
	stack = [capture, timer, fps_counter, camera]
	setup = setup_stack(stack)(setup)
	render = render_stack(stack)(render)
	
	window = Window(setup, render,
		size=projection_size, title="Projection",
		monitor=monitor_name, maximize=maximize_window)
	
	main_loop(window)
