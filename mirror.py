import cv2 as cv
import _config as config
from cyberdesk.calibration import load_calibration
from cyberdesk.math import rect_corners
from cyberdesk.graphics3d import create_texture, update_texture, draw_texture
from cyberdesk.app import projection_main_loop, main_loop_config_args

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

def setup():
	projection_texture = create_texture(projection_size)
	
	return projection_texture

def render(projection_texture, camera_frame, **kwargs):
	output = cv.warpPerspective(camera_frame, perspective_transform, projection_size)
	output = cv.cvtColor(output, cv.COLOR_RGB2RGBA)
	
	update_texture(projection_texture, projection_size, output.view("uint32"))
	draw_texture(projection_texture, projection_rect)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
