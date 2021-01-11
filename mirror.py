from src import *
import cv2 as cv
import _config as config

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

def render(projection_texture, camera_frame):
	output = cv.warpPerspective(camera_frame, perspective_transform, projection_size)
	output = cv.cvtColor(output, cv.COLOR_RGB2RGBA)
	output = cv_to_np(output)
	
	update_texture(projection_texture, projection_size, output)
	draw_texture(projection_texture, projection_rect)

if __name__ == "__main__":
	projection_main_loop(render, projection_size,
		monitor_name=config.monitor_name)
