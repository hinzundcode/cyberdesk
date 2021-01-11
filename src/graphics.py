class Color:
	BLACK = (0, 0, 0)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	YELLOW = (255, 255, 0)
	CYAN = (0, 255, 255)
	MAGENTA = (255, 0, 255)
	WHITE = (255, 255, 255)

def draw_chessboard(ctx, size, field_size=80, border=80):
	ctx.set_source_rgba(1, 1, 1, 1)
	ctx.rectangle(0, 0, *size)
	ctx.fill()
	
	for y in range(0+border, size[1]-border, field_size):
		i = y // field_size
		if i % 2 == 0:
			start = field_size
		else:
			start = 0
		for x in range(start+border, size[0]-border, field_size*2):
			ctx.set_source_rgba(0, 0, 0, 1)
			ctx.rectangle(x, y, field_size, field_size)
			ctx.fill()
