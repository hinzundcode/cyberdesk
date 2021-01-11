import cv2 as cv
import cv2.aruco as aruco
import os

def main():
	count = 100
	size = 200
	path = "markers/4x4"
	
	os.makedirs(path, exist_ok=True)
	
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
	for i in range(0, count):
		image = aruco.drawMarker(aruco_dict, i, size)
		cv.imwrite("{}/{:02d}.png".format(path, i), image)

if __name__ == "__main__":
	main()
