import numpy as np
from OpenGL.GL import GL_BGR, GL_UNSIGNED_BYTE
import cv2 as cv
from cyberdesk.graphics3d import Texture, Material, QuadGeometry, quad_shader
from cyberdesk.app import projection, run

@projection
def mirror(camera_size, projection_rect, perspective_transform, **kwargs):
	texture = Texture(camera_size, format=GL_BGR, type=GL_UNSIGNED_BYTE)
	material = Material(shader=quad_shader(), texture=texture)
	corners = cv.perspectiveTransform(np.array([projection_rect], dtype="float32"), perspective_transform)[0]
	geometry = QuadGeometry(corners)
	
	def render(camera_frame, camera, **kwargs):
		texture.update(camera_frame)
		camera.render(geometry, material)
	
	return render

if __name__ == "__main__":
	run(mirror)
