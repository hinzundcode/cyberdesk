import glfw
from enum import IntEnum

class GamepadButton(IntEnum):
	A = glfw.GAMEPAD_BUTTON_A
	B = glfw.GAMEPAD_BUTTON_B
	X = glfw.GAMEPAD_BUTTON_X
	Y = glfw.GAMEPAD_BUTTON_Y
	LEFT_SHOULDER = glfw.GAMEPAD_BUTTON_LEFT_BUMPER
	RIGHT_SHOULDER = glfw.GAMEPAD_BUTTON_RIGHT_BUMPER
	LEFT_STICK = glfw.GAMEPAD_BUTTON_LEFT_THUMB
	RIGHT_STICK = glfw.GAMEPAD_BUTTON_RIGHT_THUMB
	SELECT = glfw.GAMEPAD_BUTTON_BACK
	START = glfw.GAMEPAD_BUTTON_START
	HOME = glfw.GAMEPAD_BUTTON_GUIDE
	UP = glfw.GAMEPAD_BUTTON_DPAD_UP
	RIGHT = glfw.GAMEPAD_BUTTON_DPAD_RIGHT
	DOWN = glfw.GAMEPAD_BUTTON_DPAD_DOWN
	LEFT = glfw.GAMEPAD_BUTTON_DPAD_LEFT

class GamepadAxis(IntEnum):
	LEFT_STICK_X = glfw.GAMEPAD_AXIS_LEFT_X
	LEFT_STICK_Y = glfw.GAMEPAD_AXIS_LEFT_Y
	RIGHT_STICK_X = glfw.GAMEPAD_AXIS_RIGHT_X
	RIGHT_STICK_Y = glfw.GAMEPAD_AXIS_RIGHT_Y
	LEFT_TRIGGER = glfw.GAMEPAD_AXIS_LEFT_TRIGGER
	RIGHT_TRIGGER = glfw.GAMEPAD_AXIS_RIGHT_TRIGGER

class Gamepad:
	def __init__(self, gamepad_id):
		self.gamepad_id = gamepad_id
		self.state_before = None
		self.state = None
	
	@property
	def present(self):
		return bool(glfw.joystick_present(self.gamepad_id))
	
	@property
	def name(self):
		return glfw.get_gamepad_name(self.gamepad_id)
	
	def update(self):
		self.state_before = self.state
		self.state = glfw.get_gamepad_state(self.gamepad_id)
	
	def get_axis(self, axis):
		if self.state is None:
			if axis == GamepadAxis.LEFT_TRIGGER or axis == GamepadAxis.RIGHT_TRIGGER:
				return -1
			else:
				return 0
		
		return self.state.axes[axis]
	
	def get_button(self, button):
		if self.state is None:
			return False
		
		return bool(self.state.buttons[button])
	
	def get_button_down(self, button):
		if self.state is None or self.state_before is None:
			return False
		
		return self.state.buttons[button] and not self.state_before.buttons[button]
	
	def get_button_up(self, button):
		if self.state is None or self.state_before is None:
			return False
		
		return not self.state.buttons[button] and self.state_before.buttons[button]
