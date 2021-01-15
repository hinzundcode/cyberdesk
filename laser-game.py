import numpy as np
from src import *
import cv2 as cv
import _config as config
import cairo
import math
import random

class Mirror:
	def __init__(self, left_id, right_id):
		self.left_id = left_id
		self.right_id = right_id
		self.left = None
		self.right = None
		self.present = False
		self.colliders = [LineCollider(None, None, self)]
	
	def update(self, left_marker, right_marker):
		if left_marker.present and right_marker.present:
			self.left = (left_marker.corners[1]+left_marker.corners[2])/2
			self.right = (right_marker.corners[0]+right_marker.corners[3])/2
			self.colliders[0].left = self.left
			self.colliders[0].right = self.right
			self.present = True

class Laser:
	def __init__(self, position, direction, target, color):
		self.position = position
		self.direction = direction
		self.target = target
		self.color = color
		self.target_corners = centered_rect_corners(target, size=(40, 40))
		self.colliders = [
			LineCollider(self.target_corners[0], self.target_corners[1], self),
			LineCollider(self.target_corners[1], self.target_corners[2], self),
			LineCollider(self.target_corners[2], self.target_corners[3], self),
			LineCollider(self.target_corners[3], self.target_corners[0], self),
		]

def calculate_laser_path(position, direction, colliders, length=100, max_bounces=10):
	targets_hit = []
	
	path = []
	ignore_collider = None	
	for i in range(0, max_bounces):
		hit = raycast(position, direction, [c for c in colliders if c != ignore_collider], length)
		if hit is not None:
			collision, collider = hit
			
			path.append((position, collision))
			
			if isinstance(collider.object, Laser):
				targets_hit.append(collider.object)
				break
			else:
				ba = collider.right-collider.left
				normal = normalize(np.array([-ba[1], ba[0]]))
				
				l = normalize(position - collision)
				reflection = normalize(2*np.dot(normal, l)*normal-l)
				
				position = collision
				direction = reflection
				ignore_collider = collider
		else:
			path.append((position, position+direction*length))
			break
	
	return path, targets_hit

projection_corners_on_camera = load_calibration()["projection_corners_on_camera"]
camera_size = config.camera_size
projection_size = config.projection_size
projection_rect = rect_corners(size=projection_size)

perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)

safe_game_area = [
	int(max(projection_corners_on_camera[0][0], projection_corners_on_camera[3][0])), #left
	int(min(projection_corners_on_camera[1][0], projection_corners_on_camera[2][0])), #right
	int(max(projection_corners_on_camera[0][1], projection_corners_on_camera[1][1])), #top
	int(min(projection_corners_on_camera[3][1], projection_corners_on_camera[2][1])), #bottom
]

def random_position():
	border = 100
	left, right, top, bottom = safe_game_area
	return np.array([
		random.randint(left+border, right-border),
		random.randint(top+border, bottom-border),
	])

def random_direction():
	return normalize(np.random.rand(2))

lasers = [
	Laser(random_position(), random_direction(), target=random_position(), color=Color.GREEN),
	Laser(random_position(), random_direction(), target=random_position(), color=Color.BLUE),
]

mirrors = [
	Mirror(8, 9),
	Mirror(10, 11),
]

def draw(ctx, mirrors, lasers, laser_paths, laser_target_hit):
	ctx.set_source_rgba(0, 0, 0, 1)
	ctx.rectangle(0, 0, *camera_size)
	ctx.fill()
	
	for mirror in mirrors:
		if mirror.present:
			ctx.set_source_rgb(*Color.WHITE)
			ctx.set_line_width(5)
			ctx.move_to(*mirror.left)
			ctx.line_to(*mirror.right)
			ctx.stroke()
	
	for i, laser in enumerate(lasers):
		ctx.set_source_rgb(*laser.color)
		ctx.set_line_width(5)
		
		for segment in laser_paths[i]:
			ctx.move_to(*segment[0])
			ctx.line_to(*segment[1])
			ctx.stroke()
		
		set_path_from_corners(ctx, laser.target_corners)
		if laser_target_hit[i]:
			ctx.fill()
		else:
			ctx.stroke()
		
		ctx.set_source_rgb(*Color.RED)
		ctx.set_line_width(20)
		ctx.move_to(*laser.position)
		ctx.rel_line_to(*(-laser.direction*40))
		ctx.stroke()

def setup():
	projection_texture = create_texture(projection_size)
	
	surface_data = np.empty(shape=camera_size, dtype=np.uint32)
	surface = cairo.ImageSurface.create_for_data(surface_data, cairo.FORMAT_ARGB32, *camera_size)
	ctx = cairo.Context(surface)
	
	markers = MarkerTracker()
	
	return projection_texture, surface_data, ctx, markers

def render(state, camera_frame_gray, delta_time, **kwargs):
	projection_texture, surface_data, ctx, markers = state
	
	markers.process_frame(*detect_markers(camera_frame_gray))
	
	for mirror in mirrors:
		left = markers.get(mirror.left_id)
		right = markers.get(mirror.right_id)
		mirror.update(left, right)
	
	colliders = []
	for laser in lasers:
		colliders += laser.colliders
	for mirror in mirrors:
		if mirror.present:
			colliders += mirror.colliders
	
	laser_paths = []
	laser_target_hit = []
	
	for laser in lasers:
		path, targets_hit = calculate_laser_path(laser.position, laser.direction, colliders, length=2000)
		laser_paths.append(path)
		laser_target_hit.append(laser in targets_hit)
	
	draw(ctx, mirrors, lasers, laser_paths, laser_target_hit)
	cv_in = surface_data.view("uint8").reshape((camera_size[1], camera_size[0], 4))
	cv_out = cv.warpPerspective(cv_in, perspective_transform, projection_size)
	cv_out = cv_out.view("uint32")
	
	update_texture(projection_texture, projection_size, cv_out)
	draw_texture(projection_texture, projection_rect)

if __name__ == "__main__":
	projection_main_loop(setup, render,
		projection_size, camera_size,
		monitor_name=config.monitor_name)
