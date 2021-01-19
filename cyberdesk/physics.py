from cyberdesk.math import line_intersection, distance_squared

class LineCollider:
	def __init__(self, left, right, object=None):
		self.left = left
		self.right = right
		self.object = object

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
