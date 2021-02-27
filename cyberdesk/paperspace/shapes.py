import numpy as np
import time

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3

class RectShape:
	def __init__(self, markers, smooth=True):
		self.markers = markers
		self.corners = None
		self.present = False
		self.smooth = smooth
	
	@property
	def markers_present(self):
		return sum(1 for marker in self.markers if marker.present)
	
	def update(self):
		tl, tr, br, bl = [(m.corners[0] if m.corners is not None else None) for m in self.markers]
		
		# if markers have not moved, keep old position
		if self.present and self.markers_present > 0 and not corners_moved([tl, tr, br, bl], self.corners):
			return
		
		# calculate 4th corner if only 3 markers are present
		if self.markers_present == 3:
			if not self.markers[TOP_LEFT].present:
				tl = br + (bl - br) + (tr - br)
			elif not self.markers[TOP_RIGHT].present:
				tr = bl + (br - bl) + (tl - bl)
			elif not self.markers[BOTTOM_LEFT].present:
				bl = tr + (tl - tr) + (br - tr)
			elif not self.markers[BOTTOM_RIGHT].present:
				br = tl + (tr - tl) + (bl - tl)
		
		if self.markers_present == 3 or self.markers_present == 4:
			corners = np.array([tl, tr, br, bl])
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

def corners_moved(new_corners, old_corners, min_diff=2):
	for i, corners in enumerate(new_corners):
		if corners is not None:
			diff = np.abs(old_corners[i] - corners).max()
			if diff >= min_diff:
				print("diff", diff)
				return True
	
	return False

def smooth_corners(new_corners, old_corners, min_diff=2):
	if old_corners is None:
		return new_corners
	
	diff = np.abs(old_corners - new_corners).max()
	if diff >= min_diff:
		return new_corners
	else:
		return old_corners
