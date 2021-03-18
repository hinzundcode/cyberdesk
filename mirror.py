import numpy as np
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
import cv2 as cv
import _config as config
from cyberdesk.calibration import load_calibration
from cyberdesk.math import rect_corners
from cyberdesk.graphics3d import Texture, Material, QuadGeometry, quad_shader
from cyberdesk.app import projection_main_loop, main_loop_config_args

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

def setup(**kwargs):
	texture = Texture(camera_size, format=GL_BGR, type=GL_UNSIGNED_BYTE)
	material = Material(shader=quad_shader(), texture=texture)
	corners = cv.perspectiveTransform(np.array([projection_rect], dtype="float32"), perspective_transform)[0]
	geometry = QuadGeometry(corners)
	
	return texture, material, geometry

def render(state, camera_frame, camera, **kwargs):
	texture, material, geometry = state
	texture.update(camera_frame)
	camera.render(geometry, material)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
