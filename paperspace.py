import os
import json
from cyberdesk.vision import MarkerTracker, detect_markers
from cyberdesk.app import projection, run
from cyberdesk.paperspace import Space
from cyberdesk.paperspace.papers import parse_paper_json

@projection
def paperspace(camera_size, perspective_transform, **kwargs):
	markers = MarkerTracker()
	
	space = Space(camera_size, perspective_transform)
	
	if not os.path.exists("papers.json"):
		print('papers.json not found. create some papers with "python create-papers.py" first')
		sys.exit(1)
	
	with open("papers.json", "r") as file:
		for data in json.load(file):
			space.add_paper(data["id"], parse_paper_json(data, markers))
	
	def render(camera, camera_frame, camera_frame_gray, **kwargs):
		markers.process_frame(*detect_markers(camera_frame_gray))
		
		space.camera = camera
		space.current_camera_frame = camera_frame
		
		space.update()
		space.render()
	
	return render

if __name__ == "__main__":
	run(paperspace)
