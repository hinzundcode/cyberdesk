import numpy as np
import cv2 as cv
import cairo
import math
import _config as config
from cyberdesk.calibration import load_calibration
from cyberdesk.math import rect_corners, get_center
from cyberdesk.graphics3d import CanvasTexture, QuadGeometry, Material, quad_shader
from cyberdesk.app import projection_main_loop, main_loop_config_args
from cyberdesk.vision import detect_markers
from cyberdesk import Color

marker_colors = {
	"0": Color.BLACK,
	"1": Color.RED,
	"2": Color.GREEN,
	"3": Color.BLUE,
	"4": Color.YELLOW,
	"5": Color.CYAN,
	"6": Color.MAGENTA,
	"7": Color.WHITE,
}

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

def draw(ctx, marker_corners, marker_ids):
	if marker_ids is not None:
		for i in range(len(marker_ids)):
			marker_id = str(marker_ids[i][0])
			
			if marker_id in marker_colors:
				corners = cv.perspectiveTransform(np.array([marker_corners[i][0]], dtype="float32"), perspective_transform)[0]
				
				radius = 10
				if marker_id == "0":
					radius = 30
				
				ctx.set_source_rgb(*marker_colors[marker_id])
				ctx.arc(*get_center(corners), radius, 0, 2*math.pi)
				ctx.fill()

def setup(**kwargs):
	canvas = CanvasTexture(projection_size)
	material = Material(shader=quad_shader(), texture=canvas.texture)
	geometry = QuadGeometry(projection_rect)
	
	return canvas, material, geometry

def render(state, camera_frame_gray, camera, **kwargs):
	canvas, material, geometry = state
	
	marker_corners, marker_ids = detect_markers(camera_frame_gray)
	
	draw(canvas.ctx, marker_corners, marker_ids)
	
	canvas.update()
	camera.render(geometry, material)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
