import numpy as np
import time

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

def smooth_corners(new_corners, old_corners, min_diff=2):
	if old_corners is None:
		return new_corners
	
	diff = np.abs(old_corners - new_corners).max()
	if diff >= min_diff:
		return new_corners
	else:
		return old_corners
