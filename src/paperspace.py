import numpy as np
import cv2 as cv

class Space:
	def __init__(self, projection_corners_on_camera, projection_rect):
		self.papers = []
		self.perspective_transform = cv.getPerspectiveTransform(projection_corners_on_camera, projection_rect)
	
	def add_paper(self, paper):
		paper.space = self
		self.papers.append(paper)
	
	def update(self):
		for paper in self.papers:
			paper.shape.update()
			if not paper.visible and paper.shape.present:
				print("show paper", paper)
				paper.show()
				paper.visible = True
			if paper.visible and not paper.shape.present:
				print("hide paper", paper)
				paper.hide()
				paper.visible = False
		
		for paper in self.papers:
			if paper.visible:
				paper.update()
	
	def render(self):
		for paper in self.papers:
			if paper.visible:
				paper.render()
	
	def project_corners(self, corners):
		return cv.perspectiveTransform(np.array([corners], dtype="float32"), self.perspective_transform)[0]

class RectShape:
	def __init__(self, markers):
		self.markers = markers
		self.corners = None
		self.present = False
	
	def update(self):
		tl, tr, br, bl = self.markers
		
		if tl.present and tr.present and br.present and bl.present:
			self.corners = [tl.corners[0], tr.corners[0], br.corners[0], bl.corners[0]]
			self.present = True
		else:
			self.present = False
	
	def __str__(self):
		return "RectShape({},{},{},{})".format(*[marker.id for marker in self.markers])

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
