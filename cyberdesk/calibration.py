import numpy as np
import os

def load_calibration(file_name="calibration.npz"):
	if not os.path.exists(file_name):
		print('calibration data not found. run "python calibrate.py" first')
		sys.exit(1)
	
	return np.load(file_name)

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
