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

def rotation_matrix(angle):
	sin = np.sin(angle)
	cos = np.cos(angle)
	
	return np.array([
		[cos, -sin],
		[sin, cos]
	], dtype="float32")

def centered_rect_corners(position, size, rotation=0):
	width = np.array([size[0], 0])
	height = np.array([0, size[1]])
	
	corners = np.array([
		position - width/2 - height/2,
		position + width/2 - height/2,
		position + width/2 + height/2,
		position - width/2 + height/2,
	], dtype="float32")
	
	if rotation != 0:
		m = rotation_matrix(np.radians(rotation))
		center = position
		for i in range(len(corners)):
			corners[i] = np.dot(m, corners[i] - center) + center
	
	return corners

def scale_polygon(corners, scale):
	corners = np.array(corners)
	center = np.average(corners, axis=0)
	return (corners - center) * scale + center

def line_intersection(a, b, c, d):
	ab = -a+b
	cd = -c+d
	
	coeffs = np.array([[ab[0], -cd[0]], [ab[1], -cd[1]]])
	right = c-a
	try:
		solution = np.linalg.solve(coeffs, right)
	except np.linalg.LinAlgError:
		return None
	
	if 0 <= solution[0]  and solution[0] <= 1 and 0 <= solution[1] and solution[1] <= 1:
		return a + ab*solution[0]
	else:
		return None

def line_center(a, b):
	return np.array([
		(a[0] + b[0])/2,
		(a[1] + b[1])/2,
	])

def distance_squared(a, b):
	return (b[0] - a[0])**2 + (b[1] - a[1])**2

def distance(a, b):
	return np.sqrt(distance_squared(a, b))

def get_center(corners):
	x = [c[0] for c in corners]
	y = [c[1] for c in corners]
	return (sum(x) / len(corners), sum(y) / len(corners))

def rotation_from_corners(corners):
	tl, tr, br, bl = corners
	diffs = tl - bl
	angle = np.degrees(np.arctan(diffs[0]/(diffs[1] + np.finfo(float).eps)))
	if diffs[1] < 0:
		angle += 180
	elif diffs[0] < 0:
		angle += 360
	
	return (180 - angle) % 360 # turn upside down
