import numpy as np
import cv2 as cv
import cairo
import math
import _config as config
from cyberdesk.calibration import load_calibration
from cyberdesk.math import rect_corners
from cyberdesk.graphics3d import CanvasTexture, QuadGeometry, Material, quad_shader
from cyberdesk.vision import detect_markers
from cyberdesk.app import projection_main_loop, main_loop_config_args
from cyberdesk import Color

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

def get_rightmost_corner(corners):
	corner = corners[0]
	for c in corners:
		if c[0] > corner[0]:
			corner = c
	return corner

def draw(canvas, marker_corners, marker_ids):
	ctx = canvas.ctx
	ctx.set_source_rgba(0, 0, 0, 1)
	ctx.rectangle(0, 0, *canvas.size)
	ctx.fill()
	
	if marker_ids is not None:
		for i in range(len(marker_ids)):
			marker_id = int(marker_ids[i][0])
			corners = cv.perspectiveTransform(np.array([marker_corners[i][0]], dtype="float32"), perspective_transform)[0]
			
			ctx.set_source_rgb(*Color.BLUE)
			ctx.set_line_width(10)
			ctx.new_path()
			for point in corners:
				ctx.line_to(*point)
			ctx.close_path()
			ctx.stroke()
			
			ctx.set_source_rgb(*Color.RED)
			ctx.arc(*corners[0], 5, 0, 2*math.pi)
			ctx.fill()
			
			ctx.set_source_rgb(*Color.BLUE)
			ctx.set_font_size(20)
			ctx.move_to(*get_rightmost_corner(corners) + np.array([10, 0]))
			ctx.show_text(str(marker_id))

def setup(**kwargs):
	canvas = CanvasTexture(projection_size)
	material = Material(shader=quad_shader(), texture=canvas.texture)
	geometry = QuadGeometry(projection_rect)
	
	return canvas, material, geometry

def render(state, camera_frame_gray, camera, **kwargs):
	canvas, material, geometry = state
	
	marker_corners, marker_ids = detect_markers(camera_frame_gray)
	
	draw(canvas, marker_corners, marker_ids)
	
	canvas.update()
	camera.render(geometry, material)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		**main_loop_config_args(config))
