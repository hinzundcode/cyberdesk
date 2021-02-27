import numpy as np
import cv2 as cv
import cairo
import time
from cyberdesk.graphics2d import create_monochrome_surface, draw_image
from cyberdesk.graphics3d import Texture

class Space:
	def __init__(self, projection_corners_on_camera, camera_size, projection_rect):
		self.papers = {}
		self.camera_size = camera_size
		self.perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)
		self.current_camera_frame = None
	
	def add_paper(self, paper_id, paper):
		paper.space = self
		self.papers[paper_id] = paper
	
	def get_paper(self, paper_id):
		return self.papers.get(paper_id)
	
	def get_papers_of_type(self, paper_type):
		return [paper for paper in self.papers.values() if isinstance(paper, paper_type)]
	
	def update(self):
		for paper in self.papers.values():
			paper.shape.update()
			if not paper.visible and paper.shape.present:
				print("show paper", paper)
				paper.show()
				paper.visible = True
			if paper.visible and not paper.shape.present:
				print("hide paper", paper)
				paper.hide()
				paper.visible = False
		
		for paper in self.papers.values():
			if paper.visible:
				paper.update()
	
	def render(self):
		for paper in self.papers.values():
			if paper.visible:
				paper.render()
	
	def project_corners(self, corners):
		return cv.perspectiveTransform(np.array([corners], dtype="float32"), self.perspective_transform)[0]

class RectShape:
	def __init__(self, markers, smooth=True):
		self.markers = markers
		self.corners = None
		self.present = False
		self.smooth = smooth
	
	def update(self):
		tl, tr, br, bl = self.markers
		
		if tl.present and tr.present and br.present and bl.present:
			corners = np.array([tl.corners[0], tr.corners[0], br.corners[0], bl.corners[0]])
			self.corners = smooth_corners(corners, self.corners) if self.smooth else corners
			self.present = True
		else:
			self.present = False
	
	def __str__(self):
		return "RectShape({},{},{},{})".format(*[marker.id for marker in self.markers])

class SingleShape:
	def __init__(self, marker, absent_after=None, smooth=True):
		self.marker = marker
		self.absent_after = absent_after
		self.corners = None
		self.present = False
		self.smooth = smooth
		self.ignore_absence_until = None
	
	def update(self):
		if self.absent_after != None and self.marker.absent_time != None:
			self.present = self.marker.absent_time < self.absent_after
		else:
			self.present = self.marker.present
		
		if self.present:
			if self.smooth:
				self.corners = smooth_corners(self.marker.corners, self.corners)
			else:
				self.corners = self.marker.corners
		
		if self.ignore_absence_until != None:
			if time.time() < self.ignore_absence_until:
				self.present = True
			else:
				self.ignore_absence_until = None
	
	def ignore_absence(self, seconds):
		self.ignore_absence_until = time.time() + seconds
	
	def __str__(self):
		return "SingleShape({})".format(self.marker.id)

class Paper:
	def __init__(self, shape):
		self.shape = shape
		self.space = None
		self.visible = False
	
	def show(self):
		pass
	
	def update(self):
		pass
	
	def render(self):
		pass
	
	def hide(self):
		pass
	
	def __str__(self):
		return "{}(shape={})".format(type(self).__name__, str(self.shape))

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

class CanvasTexture:
	def __init__(self, size):
		self.size = size
		self.texture = Texture(size)
		self.data = np.zeros(shape=size, dtype=np.uint32)
		self.surface = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_ARGB32, *size)
		self.ctx = cairo.Context(self.surface)
	
	def draw(self, corners):
		self.texture.update(self.data)
		self.texture.draw(corners)

def smooth_corners(new_corners, old_corners, min_diff=2):
	if old_corners is None:
		return new_corners
	
	diff = np.abs(old_corners - new_corners).max()
	if diff >= min_diff:
		return new_corners
	else:
		return old_corners
