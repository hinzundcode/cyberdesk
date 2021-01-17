import numpy as np
import cv2.aruco as aruco
import cairo

DIN_A4_WIDTH_MM = 210
DIN_A4_HEIGHT_MM = 297
DIN_A4_WIDTH_POINTS = 595
DIN_A4_HEIGHT_POINTS = 842

def mm_to_points(x, page_width_mm=DIN_A4_WIDTH_MM, page_width_points=DIN_A4_WIDTH_POINTS):
	return x * page_width_points/page_width_mm

def create_monochrome_surface(img, size, rot90=0):
	img = 255-img # invert
	if rot90 > 0:
		img = np.rot90(img, rot90, axes=(1, 0)).copy(order="C")
	return cairo.ImageSurface.create_for_data(img, cairo.FORMAT_A8, *size)

def draw_image(ctx, img, position, size):
	scale_x = size[0] / img.get_width()
	scale_y = size[1] / img.get_height()
	
	ctx.save()
	ctx.translate(*position)
	ctx.scale(scale_x, scale_y)
	ctx.set_source_surface(img)
	ctx.paint()
	ctx.restore()

def get_marker_images(*marker_ids):
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
	return [aruco.drawMarker(aruco_dict, marker_id, 200) for marker_id in marker_ids]

def draw_rect_portrait_a4(ctx, markers, title=""):
	tl = create_monochrome_surface(markers[0], markers[0].shape, 0)
	tr = create_monochrome_surface(markers[1], markers[1].shape, 1)
	br = create_monochrome_surface(markers[2], markers[2].shape, 2)
	bl = create_monochrome_surface(markers[3], markers[3].shape, 3)
	
	page_size = (DIN_A4_WIDTH_MM, DIN_A4_HEIGHT_MM)
	border = (10, 10)
	marker_size = (30, 30)

	tl_pos = (border[0], border[1])
	tr_pos = (page_size[0] - marker_size[0] - border[0], border[1])
	br_pos = (page_size[0] - marker_size[0] - border[0], page_size[1] - marker_size[1] - border[1])
	bl_pos = (border[0], page_size[1] - marker_size[1] - border[1])

	marker_size_points = (mm_to_points(marker_size[0]), mm_to_points(marker_size[1]))
	
	draw_image(ctx, tl, (mm_to_points(tl_pos[0]), mm_to_points(tl_pos[1])), marker_size_points)
	draw_image(ctx, tr, (mm_to_points(tr_pos[0]), mm_to_points(tr_pos[1])), marker_size_points)
	draw_image(ctx, br, (mm_to_points(br_pos[0]), mm_to_points(br_pos[1])), marker_size_points)
	draw_image(ctx, bl, (mm_to_points(bl_pos[0]), mm_to_points(bl_pos[1])), marker_size_points)
	
	if title != "":
		ctx.set_font_size(15)
		extents = ctx.text_extents(title)
		ctx.move_to(
			mm_to_points(page_size[0]/2) - extents.width/2,
			mm_to_points(page_size[1] - border[1]/2)
		)
		ctx.show_text(title)
