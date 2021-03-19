from cyberdesk.paperspace.shapes import RectShape, SingleShape

from .video import VideoPaper
from .portals import PortalIn, PortalOut
from .gamepad import GamepadPaper
from .python import PythonPaper
from .zigbee import ShortcutButton

def parse_paper_json(data, markers):
	paper = None
	
	if data["type"] == "video":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = VideoPaper(shape, tuple(data["video_size"]), data["video_file"])
	elif data["type"] == "portal-in":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = PortalIn(shape)
	elif data["type"] == "portal-out":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = PortalOut(shape)
	elif data["type"] == "gamepad":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = GamepadPaper(shape, data["gamepad_id"])
	elif data["type"] == "python":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = PythonPaper(shape, data["filename"])
	elif data["type"] == "shortcut-button":
		shape = SingleShape(markers.get_all(*data["markers"])[0], absent_after=1)
		paper = ShortcutButton(shape, data["mqtt_topic"], data["mqtt_host"])
	
	return paper
