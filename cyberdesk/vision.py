import cv2 as cv
import cv2.aruco as aruco

def get_camera_capture(width, height, camera_id=0):
	cap = cv.VideoCapture(camera_id)
	cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
	print(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	print(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
	print(cap.get(cv.CAP_PROP_FPS))
	return cap

def get_camera_frame(cap, flip=-1):
	ret, frame = cap.read()
	frame = cv.flip(frame, flip)
	gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	return frame, gray

def detect_markers(gray):
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
	params = aruco.DetectorParameters_create()
	params.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
	corners, ids, rejectedImgPoints = aruco.detectMarkers(
		gray, aruco_dict, parameters=params)
	
	return corners, ids

class Marker:
	def __init__(self, id):
		self.id = id
		self.corners = None
		self.absent_frames = None
	
	@property
	def present(self):
		return self.absent_frames == 0

class MarkerTracker:
	def __init__(self):
		self.markers = {}
	
	def process_frame(self, marker_corners, marker_ids):
		for _, marker in self.markers.items():
			if marker.absent_frames != None:
				marker.absent_frames += 1
		
		if marker_ids is not None:
			for i in range(len(marker_ids)):
				marker_id = str(marker_ids[i][0])
				corners = marker_corners[i][0]
				marker = self.get(marker_id)
				marker.corners = corners
				marker.absent_frames = 0
	
	def get(self, marker_id):
		marker_id = str(marker_id)
		
		if marker_id not in self.markers:
			self.markers[marker_id] = Marker(marker_id)
		
		return self.markers[marker_id]
	
	def get_all(self, *marker_ids):
		return list(map(self.get, marker_ids))

def get_marker_images(*marker_ids):
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
	return [aruco.drawMarker(aruco_dict, marker_id, 200) for marker_id in marker_ids]
