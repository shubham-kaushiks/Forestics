import sys

# sys.stdin=open("input", "r")
sys.stdout=open("output", "w")

# from mapbox import Maps
from mapbox import Static
import pymongo


####################################################
# DO NOT UPLOAD DIRECTLY, PERSONAL ACCESS TOKEN HERE
# FOR DEVELOPMENT PURPOSES ONLY
#
#
#
import os
os.environ['MAPBOX_ACCESS_TOKEN'] = #insert MapBoxAccessToken Here
#
#
#
#
####################################################

# maps = Maps()
service = Static()

# response = maps.tile("mapbox.satellite", *deg2num(22.3370281, 80.5951098, 12))

mclient = pymongo.MongoClient("mongodb://localhost:27017/")

db = mclient["forestics"]
col = db["imgdata"]

zoomLevel = 12
# [ [lat, long] ]
coords = [
	[22.3379759, 80.5939463],
	[22.3379759, 82.5939463],
	[20.3379759, 82.5939463]
]

for coord in coords:
	response = service.image("mapbox.satellite", lon=coord[1], lat=coord[0], z=zoomLevel)
	print(response.status_code)
	if response.status_code == 200:
		print("Data retrieval succesful.")
		imgd = {"lat": coord[0], "lon": coord[1], "blob": response.content}
		col.insert_one(imgd)
		# with open("./output.png", "wb") as out:
		# 	out.write(response.content)
	else:
		print("Error in data retrieval. Exiting.")
		exit(0)

print("Data inserted into mongodb.")

# for coord in col.find({}, {"lat": 1, "lon": 1}):
	# print(coord)

import cv2 as cv
import numpy as np


def findAcc(img, nam):
	low_green = np.array([0, 80, 0])
	high_green = np.array([255, 255, 255])
	hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

	mask = cv.inRange(hsv_img, low_green, high_green)

	res = cv.bitwise_and(img, img, mask = mask)
	cv.imshow(str(nam+1) + " Mask", mask)
	cv.imwrite(str(nam+1) + ".png", mask)

	bw = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
	bw = cv.GaussianBlur(bw, (3, 3), 0)

	a, thresh = cv.threshold(bw, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
	kernel = np.ones((5,5), np.uint8)
	
	canny = cv.Canny(bw, a*0.5, a)
	cv.imshow(str(nam+2) + " Canny", canny)
	cv.imwrite(str(nam+2) + ".png", canny)

	canny = cv.dilate(canny, kernel, iterations=1)
	# cv.imshow("ss", canny)
	
	area, tot = cv.countNonZero(canny), img.shape[0] * img.shape[1]
	cv.putText(img, 'Forest Cover ' + str(area/tot * 100) , (56, 80), cv.FONT_HERSHEY_COMPLEX, 0.7, (2,255,2),2)
	cv.imshow(str(nam+3), img)
	cv.imwrite(str(nam+3)+'.png', img)

	return area/tot


img = cv.imread('img.png')
findAcc(img, 0)

img = cv.imread('img2.png')
findAcc(img, 3)

cv.waitKey(0)
cv.destroyAllWindows()