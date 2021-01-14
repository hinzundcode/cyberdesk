from src import *
import cv2 as cv
import _config as config
import cairo

camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)
projection_corners_on_camera = None

def draw_cv_polygon(frame, corners, color=Color.GREEN):
	corners = np.array(corners, dtype=np.int32)
	pts = corners.reshape((-1, 1, 2))
	cv.polylines(frame, [pts], True, color)
	return frame

def setup():
	surface_data = np.empty(shape=projection_size, dtype=np.uint32)
	surface = cairo.ImageSurface.create_for_data(surface_data, cairo.FORMAT_ARGB32, *projection_size)
	
	ctx = cairo.Context(surface)
	draw_chessboard(ctx, projection_size)
	
	projection_texture = create_texture(projection_size, surface_data)
	
	return projection_texture

def render(projection_texture, camera_frame, camera_frame_gray, **kwargs):
	global projection_corners_on_camera
	
	draw_texture(projection_texture, projection_rect)
	
	chessboard_size = 6, 13
	criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
	
	ret, corners = cv.findChessboardCorners(camera_frame_gray, chessboard_size, None)
	if ret:
		corners = cv.cornerSubPix(camera_frame_gray, corners, (11, 11), (-1, -1), criteria)
		
		chessboard_width, chessboard_height = chessboard_size
		
		bl_height = corners[0][0][1] - corners[1][0][1]
		bl_width = corners[chessboard_width][0][0] - corners[0][0][0]
		bl = corners[0][0] + np.array([-2*bl_width, 2*bl_height])
		
		tl_height = corners[chessboard_width-2][0][1] - corners[chessboard_width-1][0][1]
		tl_width = corners[2*chessboard_width-1][0][0] - corners[chessboard_width-1][0][0]
		tl = corners[chessboard_width-1][0] + np.array([-2*tl_width, -2*tl_height])
		
		tr_height = corners[chessboard_width*chessboard_height-2][0][1] - corners[chessboard_width*chessboard_height-1][0][1]
		tr_width = corners[chessboard_width*chessboard_height-1][0][0] - corners[chessboard_width*(chessboard_height-1)-1][0][0]
		tr = corners[chessboard_width*chessboard_height-1][0] + np.array([2*tl_width, -2*tl_height])
		
		br_height = corners[chessboard_width*(chessboard_height-1)][0][1] - corners[chessboard_width*(chessboard_height-1)+1][0][1]
		br_width = corners[chessboard_width*(chessboard_height-1)][0][0] - corners[chessboard_width*(chessboard_height-2)][0][0]
		br = corners[chessboard_width*(chessboard_height-1)][0] + np.array([2*tl_width, 2*tl_height])
		
		projection_corners_on_camera = np.array([tl, tr, br, bl], dtype="float32")
		
		projection_corners_on_camera = cv.cornerSubPix(camera_frame_gray, projection_corners_on_camera, (11, 11), (-1, -1), criteria)
		
		camera_frame = draw_cv_polygon(camera_frame, projection_corners_on_camera)
	
	camera_frame = cv.drawChessboardCorners(camera_frame, chessboard_size, corners, ret)
	cv.imshow("camera_frame", camera_frame)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		projection_size, camera_size,
		monitor_name=config.monitor_name)
	
	if projection_corners_on_camera is not None:
		np.savez("calibration.npz", projection_corners_on_camera=projection_corners_on_camera)
		
		print(projection_corners_on_camera)
		print("calibration saved!")
