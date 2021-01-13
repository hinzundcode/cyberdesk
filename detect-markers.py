from src import *
import cv2 as cv
import _config as config
import cairo
import math

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

def draw(ctx, marker_corners, marker_ids):
	ctx.set_source_rgba(0, 0, 0, 1)
	ctx.rectangle(0, 0, *camera_size)
	ctx.fill()
	
	if marker_ids is not None:
		for i in range(len(marker_ids)):
			marker_id = int(marker_ids[i][0])
			corners = marker_corners[i][0]
			
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

def setup():
	projection_texture = create_texture(projection_size)
	
	surface_data = np.empty(shape=camera_size, dtype=np.uint32)
	surface = cairo.ImageSurface.create_for_data(surface_data, cairo.FORMAT_ARGB32, *camera_size)
	ctx = cairo.Context(surface)
	
	return projection_texture, surface_data, ctx

def render(state, camera_frame, camera_frame_gray):
	projection_texture, surface_data, ctx = state
	
	marker_corners, marker_ids = detect_markers(camera_frame_gray)
	
	draw(ctx, marker_corners, marker_ids)
	cv_in = surface_data.view("uint8").reshape((camera_size[1], camera_size[0], 4))
	cv_out = cv.warpPerspective(cv_in, perspective_transform, projection_size)
	cv_out = cv_out.view("uint32")
	
	update_texture(projection_texture, projection_size, cv_out)
	draw_texture(projection_texture, projection_rect)

if __name__ == "__main__":
	projection_main_loop(setup, render, projection_size,
		monitor_name=config.monitor_name)
