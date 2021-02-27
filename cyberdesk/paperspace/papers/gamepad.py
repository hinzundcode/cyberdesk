import numpy as np
import glfw
import math
from enum import IntEnum
from cyberdesk.paperspace import Paper
from cyberdesk.graphics2d import draw_text_centered
from cyberdesk.graphics3d import CanvasTexture
from cyberdesk.input import Gamepad, GamepadButton, GamepadAxis
from cyberdesk import Color

large_button_size = 0.6
small_button_size = 0.4
gamepad_image_buttons = [
	(np.array((2.5, 2.5)), large_button_size, GamepadButton.UP),
	(np.array((1.5, 3.5)), large_button_size, GamepadButton.LEFT),
	(np.array((2.5, 4.5)), large_button_size, GamepadButton.DOWN),
	(np.array((3.5, 3.5)), large_button_size, GamepadButton.RIGHT),
	
	(np.array((11.5, 4.5)), large_button_size, GamepadButton.A),
	(np.array((12.5, 3.5)), large_button_size, GamepadButton.B),
	(np.array((10.5, 3.5)), large_button_size, GamepadButton.X),
	(np.array((11.5, 2.5)), large_button_size, GamepadButton.Y),
	
	(np.array((6, 3.5)), small_button_size, GamepadButton.SELECT),
	(np.array((5.7, 3.5)), small_button_size, GamepadButton.SELECT),
	(np.array((8, 3.5)), small_button_size, GamepadButton.START),
	(np.array((8.3, 3.5)), small_button_size, GamepadButton.START),
	
	#(np.array((7, 7)), small_button_size, GamepadButton.HOME),
	#(np.array((7, 7)), large_button_size, GamepadButton.HOME),
]

axis_size = 1
gamepad_image_axes = [
	(np.array((5, 6)), axis_size, GamepadAxis.LEFT_STICK_X, GamepadAxis.LEFT_STICK_Y, GamepadButton.LEFT_STICK),
	(np.array((9, 6)), axis_size, GamepadAxis.RIGHT_STICK_X, GamepadAxis.RIGHT_STICK_Y, GamepadButton.RIGHT_STICK),
]

gamepad_image_shoulder_buttons = [
	(np.array((1.5, 1)), np.array((2, 0.5)), GamepadButton.LEFT_SHOULDER),
	(np.array((10.5, 1)), np.array((2, 0.5)), GamepadButton.RIGHT_SHOULDER),
]

gamepad_image_triggers = [
	(np.array((1.5, 0)), np.array((2, 0.8)), GamepadAxis.LEFT_TRIGGER),
	(np.array((10.5, 0)), np.array((2, 0.8)), GamepadAxis.RIGHT_TRIGGER),
]

dead_zone = 0.01

def draw_gamepad_image(ctx, gamepad, offset=np.array((0, 0)), scale=20,
	button_color=Color.WHITE, button_pressed_color=Color.RED):
	for pos, size, button in gamepad_image_buttons:
		pos = pos*scale + offset
		if gamepad.get_button(button):
			ctx.set_source_rgb(*button_pressed_color)
		else:
			ctx.set_source_rgb(*button_color)
		ctx.arc(*pos, size*scale, 0, 2*math.pi)
		ctx.fill()
	
	for pos, size, button in gamepad_image_shoulder_buttons:
		pos = pos*scale + offset
		size = size*scale
		if gamepad.get_button(button):
			ctx.set_source_rgb(*button_pressed_color)
		else:
			ctx.set_source_rgb(*button_color)
		ctx.rectangle(*pos, *size)
		ctx.fill()
		
	for pos, size, axis in gamepad_image_triggers:
		pos = pos*scale + offset
		size = size*scale
		value = (gamepad.get_axis(axis)+1)/2
		
		ctx.set_source_rgb(*button_color)
		ctx.rectangle(*pos, *size)
		ctx.fill()
		
		ctx.set_source_rgba(*button_pressed_color, value)
		ctx.rectangle(*pos, *size)
		ctx.fill()
	
	for pos, size, axis_x, axis_y, button in gamepad_image_axes:
		draw_pos = pos*scale + offset
		if gamepad.get_button(button):
			ctx.set_source_rgb(*button_pressed_color)
		else:
			ctx.set_source_rgb(*button_color)
		ctx.arc(*draw_pos, size*scale, 0, 2*math.pi)
		ctx.fill()
		
		x = gamepad.get_axis(axis_x)
		y = gamepad.get_axis(axis_y)
		
		if abs(x) > dead_zone or abs(y) > dead_zone:
			draw_pos = (pos + np.array((x, y))/2)*scale + offset
			ctx.set_source_rgb(*Color.RED)
			ctx.arc(*draw_pos, size*scale, 0, 2*math.pi)
			ctx.fill()

class GamepadPaper(Paper):
	def __init__(self, shape, gamepad_id):
		super().__init__(shape)
		self.gamepad_id = gamepad_id
		self.gamepad = None
		self.canvas = None
	
	def show(self):
		self.gamepad = Gamepad(self.gamepad_id-1)
		#self.canvas = CanvasTexture((400, 565))
		self.canvas = CanvasTexture((400, 280))
	
	def update(self):
		self.gamepad.update()
	
	def render(self):
		ctx = self.canvas.ctx
		
		ctx.set_source_rgb(*Color.BLACK)
		ctx.rectangle(0, 0, *self.canvas.size)
		ctx.fill()
		
		if self.gamepad.present:
			draw_gamepad_image(ctx, self.gamepad, offset=np.array((60, 60)))
		
		ctx.set_source_rgb(*Color.WHITE)
		
		if self.gamepad.present:
			draw_text_centered(ctx, self.gamepad.name, (70, 230), (255, 40), font_size=25)
		else:
			text = "Gamepad {} disconnected".format(self.gamepad_id)
			draw_text_centered(ctx, text, (0, 0), self.canvas.size, font_size=25)
		
		self.canvas.draw(self.space.project_corners(self.shape.corners))
	
	def hide(self):
		self.gamepad = None
		self.canvas = None
