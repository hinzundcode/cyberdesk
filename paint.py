import numpy as np
import cv2 as cv
import cairo
import math
from cyberdesk.math import get_center
from cyberdesk.graphics3d import CanvasTexture, QuadGeometry, Material, quad_shader
from cyberdesk.app import projection, run
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

def draw(ctx, marker_corners, marker_ids, perspective_transform):
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

@projection
def paint(projection_size, projection_rect, perspective_transform, **kwargs):
	canvas = CanvasTexture(projection_size)
	material = Material(shader=quad_shader(), texture=canvas.texture)
	geometry = QuadGeometry(projection_rect)
	
	def render(camera, camera_frame_gray, **kwargs):
		marker_corners, marker_ids = detect_markers(camera_frame_gray)
		
		draw(canvas.ctx, marker_corners, marker_ids, perspective_transform)
		
		canvas.update()
		camera.render(geometry, material)
	
	return render

if __name__ == "__main__":
	run(paint)
