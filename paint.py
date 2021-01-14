from src import *
import cv2 as cv
import _config as config
import cairo
import math

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

def get_center(corners):
	x = [c[0] for c in corners]
	y = [c[1] for c in corners]
	return (sum(x) / len(corners), sum(y) / len(corners))

def draw(ctx, marker_corners, marker_ids):
	if marker_ids is not None:
		for i in range(len(marker_ids)):
			marker_id = str(marker_ids[i][0])
			
			if marker_id in marker_colors:
				corners = marker_corners[i][0]
				
				radius = 10
				if marker_id == "0":
					radius = 30
				
				ctx.set_source_rgb(*marker_colors[marker_id])
				ctx.arc(*get_center(corners), radius, 0, 2*math.pi)
				ctx.fill()

def setup():
	projection_texture = create_texture(projection_size)
	
	surface_data = np.empty(shape=camera_size, dtype=np.uint32)
	surface = cairo.ImageSurface.create_for_data(surface_data, cairo.FORMAT_ARGB32, *camera_size)
	ctx = cairo.Context(surface)
	
	return projection_texture, surface_data, ctx

def render(state, camera_frame_gray, **kwargs):
	projection_texture, surface_data, ctx = state
	
	marker_corners, marker_ids = detect_markers(camera_frame_gray)
	
	draw(ctx, marker_corners, marker_ids)
	cv_in = surface_data.view("uint8").reshape((camera_size[1], camera_size[0], 4))
	cv_out = cv.warpPerspective(cv_in, perspective_transform, projection_size)
	cv_out = cv_out.view("uint32")
	
	update_texture(projection_texture, projection_size, cv_out)
	draw_texture(projection_texture, projection_rect)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		projection_size, camera_size,
		monitor_name=config.monitor_name)
