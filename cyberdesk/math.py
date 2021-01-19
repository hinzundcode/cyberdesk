import numpy as np

def normalize(vector):
	return vector / np.sqrt(np.sum(vector**2))

def rect_corners(size, position=(0, 0)):
	x, y = position
	width, height = size
	
	return np.array([
		[x, y],
		[x+width, y],
		[x+width, y+height],
		[x, y+height]
	], dtype="float32")

def centered_rect_corners(position, size):
	width = np.array([size[0], 0])
	height = np.array([0, size[1]])
	
	return np.array([
		position - width/2 - height/2,
		position + width/2 - height/2,
		position + width/2 + height/2,
		position - width/2 + height/2,
	], dtype="float32")

def scale_polygon(corners, scale):
	corners = np.array(corners)
	center = np.average(corners, axis=0)
	return (corners - center) * scale + center

def line_intersection(a, b, c, d):
	ab = -a+b
	cd = -c+d
	
	coeffs = np.array([[ab[0], -cd[0]], [ab[1], -cd[1]]])
	right = c-a
	solution = np.linalg.solve(coeffs, right)
	
	if 0 <= solution[0]  and solution[0] <= 1 and 0 <= solution[1] and solution[1] <= 1:
		return a + ab*solution[0]
	else:
		return None

def distance_squared(a, b):
	return (b[0] - a[0])**2 + (b[1] - a[1])**2

def get_center(corners):
	x = [c[0] for c in corners]
	y = [c[1] for c in corners]
	return (sum(x) / len(corners), sum(y) / len(corners))
