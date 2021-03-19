import numpy as np
import cv2 as cv
import cairo
from cyberdesk.calibration import draw_chessboard
from cyberdesk.graphics3d import CanvasTexture, Material, QuadGeometry, quad_shader
from cyberdesk.app import projection, run
from cyberdesk import Color

def draw_cv_polygon(frame, corners, color=Color.GREEN):
	corners = np.array(corners, dtype=np.int32)
	pts = corners.reshape((-1, 1, 2))
	cv.polylines(frame, [pts], True, color)
	return frame

@projection(load_calibration=False)
def calibration(projection_size, projection_rect, **kwargs):
	canvas = CanvasTexture(projection_size)
	draw_chessboard(canvas.ctx, projection_size)
	canvas.update()
	
	material = Material(shader=quad_shader(), texture=canvas.texture)
	geometry = QuadGeometry(projection_rect)

	def render(camera, camera_frame, camera_frame_gray, **kwargs):
		global projection_corners_on_camera
		
		camera.render(geometry, material)
		
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
	
	return render

if __name__ == "__main__":
	run(calibration)
	
	if projection_corners_on_camera is not None:
		np.savez("calibration.npz", projection_corners_on_camera=projection_corners_on_camera)
		
		print(projection_corners_on_camera)
		print("calibration saved!")
