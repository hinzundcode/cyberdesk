from cyberdesk.graphics2d import create_monochrome_surface, draw_image

DIN_A4_WIDTH_MM = 210
DIN_A4_HEIGHT_MM = 297
DIN_A4_WIDTH_POINTS = 595
DIN_A4_HEIGHT_POINTS = 842

DIN_A5_WIDTH_MM = DIN_A4_HEIGHT_MM/2
DIN_A5_HEIGHT_MM = DIN_A4_WIDTH_MM
DIN_A5_WIDTH_POINTS = 420
DIN_A5_HEIGHT_POINTS = 595

def mm_to_points(x, page_width_mm=DIN_A4_WIDTH_MM, page_width_points=DIN_A4_WIDTH_POINTS):
	return x * page_width_points/page_width_mm

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

def draw_rect_landscape_a5(ctx, markers, title=""):
	tl = create_monochrome_surface(markers[0], markers[0].shape, 0)
	tr = create_monochrome_surface(markers[1], markers[1].shape, 1)
	br = create_monochrome_surface(markers[2], markers[2].shape, 2)
	bl = create_monochrome_surface(markers[3], markers[3].shape, 3)
	
	page_size = (DIN_A4_WIDTH_MM, DIN_A4_HEIGHT_MM)
	border = (10, 10)
	marker_size = (30, 30)

	tl_pos = (border[0], border[1])
	tr_pos = (page_size[0] - marker_size[0] - border[0], border[1])
	br_pos = (page_size[0] - marker_size[0] - border[0], page_size[1]/2 - marker_size[1] - border[1])
	bl_pos = (border[0], page_size[1]/2 - marker_size[1] - border[1])

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
			mm_to_points(page_size[1]/2 - border[1]/2)
		)
		ctx.show_text(title)

def draw_single_marker(ctx, marker, size_in_cm=3):
	img = create_monochrome_surface(marker, marker.shape)
	pos_points = (mm_to_points(10), mm_to_points(10))
	marker_size_points = (mm_to_points(size_in_cm*10), mm_to_points(size_in_cm*10))
		
	draw_image(ctx, img, pos_points, marker_size_points)
