import numpy as np
import cairo

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

def set_path_from_corners(ctx, corners):
	ctx.new_path()
	for point in corners:
		ctx.line_to(*point)
	ctx.close_path()
