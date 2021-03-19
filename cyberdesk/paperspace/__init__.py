import numpy as np
import cv2 as cv

class Space:
	def __init__(self, camera_size, perspective_transform):
		self.papers = {}
		self.camera_size = camera_size
		self.perspective_transform = perspective_transform
		self.current_camera_frame = None
		self.camera = None
	
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
