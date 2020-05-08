#
# Refer below tutorial 
#
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_photo/py_inpainting/py_inpainting.html
# 
# pip install opencv-python
# 
import cv2
import numpy as np

img = cv2.imread('img.jpg')
msk = cv2.imread('imgmask.jpg', cv2.CV_8UC1) # mask must be converted to 8-bit 1-channel image

cv2.imshow('img', img)
cv2.imshow('msk', msk)

dst = cv2.inpaint(img, msk, 3, cv2.INPAINT_NS) # or cv2.INPAINT_TELEA algorithm
cv2.imshow('dst', dst)
cv2.imwrite('recovered.jpg', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

