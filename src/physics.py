import numpy as np

class LineCollider:
	def __init__(self, left, right, object=None):
		self.left = left
		self.right = right
		self.object = object

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

def raycast(position, direction, colliders, length=100):
	ray_start = position
	ray_end = position + direction*length
	
	min_distance = None
	closest_collision = None
	collider_hit = None
	
	for collider in colliders:
		collision = line_intersection(ray_start, ray_end, collider.left, collider.right)
		if collision is not None:
			distance = distance_squared(ray_start, collision)
			if min_distance == None or distance < min_distance:
				min_distance = distance
				closest_collision = collision
				collider_hit = collider
	
	if closest_collision is None:
		return None
	else:
		return closest_collision, collider_hit
