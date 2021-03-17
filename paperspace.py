import os
import json
import _config as config
from cyberdesk.calibration import load_calibration
from cyberdesk.math import rect_corners
from cyberdesk.vision import MarkerTracker, detect_markers
from cyberdesk.graphics3d import OrtographicCamera
from cyberdesk.app import projection_main_loop, main_loop_config_args
from cyberdesk.paperspace import Space
from cyberdesk.paperspace.shapes import RectShape, SingleShape
from cyberdesk.paperspace.papers.video import VideoPaper
from cyberdesk.paperspace.papers.portals import PortalIn, PortalOut
from cyberdesk.paperspace.papers.gamepad import GamepadPaper
from cyberdesk.paperspace.papers.python import PythonPaper
from cyberdesk.paperspace.papers.zigbee import ShortcutButton

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

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

def setup():
	markers = MarkerTracker()
	
	space = Space(projection_corners_on_camera, camera_size, projection_rect)
	
	if not os.path.exists("papers.json"):
		print('papers.json not found. create some papers with "python create-papers.py" first')
		sys.exit(1)
	
	with open("papers.json", "r") as file:
		for data in json.load(file):
			space.add_paper(data["id"], parse_paper_json(data, markers))
	
	return markers, space

def render(state, camera_frame, camera_frame_gray, camera, **kwargs):
	markers, space = state
	
	markers.process_frame(*detect_markers(camera_frame_gray))
	
	space.camera = camera
	space.current_camera_frame = camera_frame
	
	space.update()
	space.render()

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
