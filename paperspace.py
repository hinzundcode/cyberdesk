from src import *
import cv2 as cv
import _config as config
import json

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

def parse_paper_json(data, markers):
	paper = None
	
	if data["type"] == "video":
		shape = RectShape(markers.get_all(*data["markers"]))
		paper = VideoPaper(shape, tuple(data["video_size"]), data["video_file"])
	
	return paper

def setup():
	markers = MarkerTracker()
	
	space = Space(projection_corners_on_camera, projection_rect)
	
	if not os.path.exists("papers.json"):
		print('papers.json not found. create some papers with "python create-papers.py" first')
		sys.exit(1)
	
	with open("papers.json", "r") as file:
		for data in json.load(file):
			space.add_paper(parse_paper_json(data, markers))
	
	return markers, space

def render(state, camera_frame_gray, **kwargs):
	markers, space = state
	
	markers.process_frame(*detect_markers(camera_frame_gray))
	
	space.update()
	space.render()

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
