import numpy as np
import paho.mqtt.client as mqtt
from enum import Enum
import json
from cyberdesk.graphics3d import draw_colored_rect
from cyberdesk.paperspace import Paper
from cyberdesk.math import centered_rect_corners, get_center, distance, line_center, rotation_from_corners
from cyberdesk import Color

class ButtonEvent(Enum):
	PRESS = "on"
	HOLD = "brightness_move_up"
	HOLD_UP = "brightness_stop"

class ShortcutButton(Paper):
	def __init__(self, shape, mqtt_topic, mqtt_host):
		super().__init__(shape)
		self.mqtt_topic = mqtt_topic
		self.mqtt_host = mqtt_host
		self.events = []
		self.pressed = False
	
	def show(self):
		self.client = mqtt.Client()
		self.client.on_connect = lambda client, userdata, flags, rc : self.on_connect()
		self.client.on_message = lambda client, userdata, message : self.on_message(message)
		self.client.connect(self.mqtt_host)
		self.client.loop_start()
	
	def on_connect(self):
		self.client.subscribe(self.mqtt_topic)
	
	def on_message(self, message):
		data = json.loads(message.payload)
		if "action" in data:
			event = ButtonEvent(data["action"])
			self.events.append(event)
	
	def update(self):
		events = self.events
		self.events = []
		
		for event in events:
			if event == ButtonEvent.PRESS:
				self.pressed = True
	
	def render(self):
		tl, tr, br, bl = self.shape.corners
		
		position = get_center(self.shape.corners)
		
		size = np.mean([
			distance(tl, tr),
			distance(bl, br),
			distance(tl, bl),
			distance(tr, br),
		])
		
		top_center = line_center(tl, tr)
		
		rotation = rotation_from_corners(self.shape.corners)
		
		outer_rect = centered_rect_corners(position, (size+50, size+50), rotation=rotation)
		inner_rect = centered_rect_corners(position, (size+20, size+20), rotation=rotation)
		draw_colored_rect(self.space.project_corners(outer_rect), Color.RED if self.pressed else Color.BLUE)
		draw_colored_rect(self.space.project_corners(inner_rect), Color.BLACK)
	
	def hide(self):
		self.client.disconnect()
		self.client.loop_stop()
		self.client = None
		self.pressed = False
