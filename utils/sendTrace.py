import requests
import cv2
import numpy as np



# img is a 32 x 32 image build from a matrix of numbers

# 1. Create the black & white texture (bumpmap) :

# Increase resolution + contrast
img = cv2.resize(img, (100, 100), interpolation = cv2.INTER_NEAREST)
blur = cv2.GaussianBlur(img,(5,5),0)
ret,thresh = cv2.threshold(blur,0, 255,  cv2.THRESH_BINARY+cv2.THRESH_OTSU)
blur = cv2.GaussianBlur(thresh,(5,5),0)

# TODO : generer un nom unique pour chaque image
bumpmapfile = "bumpmap"+".png"
cv2.imwrite(bumpmapfile, blue)


# 2. Create the rgb texture :

# Skin texture masking 
skin = cv2.imread('texture.jpg')
skin = cv2.resize(skin, (100, 100), interpolation = cv2.INTER_NEAREST)
masked = cv2.bitwise_and(skin, skin, mask=cv2.bitwise_not(blur))
alpha = np.sum(masked, axis=-1) > 0

# Convert True/False to 0/255 and change type to "uint8" to match "na"
alpha = np.uint8(alpha * 255)
# Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
res = np.dstack((masked, alpha))


# TODO : generer un nom unique pour chaque image
mapfile = "map"+".png"
cv2.imwrite(mapfile, res)


files = {
	"audio" : open(audiofile, 'rb'),
	"bumpmap" : open(bumpmapfile, 'rb'),
	"map" : open(mapfile, 'rb'),
}

request.post('wunderblock.ninonlm.com', files=files)


