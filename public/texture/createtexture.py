import cv2
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

img_path = 'cv/bumpmap1234.png'
img = cv2.imread(img_path, 0)
#img =  cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


#img = cv2.resize(img, (32, 32), interpolation = cv2.INTER_AREA)

img = cv2.resize(img, (100, 100), interpolation = cv2.INTER_NEAREST)

#print(img)

blur = cv2.GaussianBlur(img,(5,5),0)
#blur = cv2.GaussianBlur(blur,(5,5),0)
ret,thresh = cv2.threshold(blur,0, 255,  cv2.THRESH_BINARY+cv2.THRESH_OTSU)

blur = cv2.GaussianBlur(thresh,(5,5),0)

backtocolor=cv2.cvtColor(blur,cv2.COLOR_GRAY2RGB)

hsv = cv2.cvtColor(backtocolor, cv2.COLOR_BGR2HSV)

cv2.imshow("Resized image", backtocolor)
cv2.waitKey(0)

#red_img  = np.full((100,100,100), (0,0,255), np.uint8)
#fused_img  = cv2.addWeighted(backtocolor, 0.8, red_img, 0.2, 0)

h, w, c = backtocolor.shape
# append Alpha channel -- required for BGRA (Blue, Green, Red, Alpha)
image_bgra = np.concatenate([backtocolor, np.full((h, w, 1), 255, dtype=np.uint8)], axis=-1)
# create a mask where white pixels ([255, 255, 255]) are True
white = np.all(backtocolor == [255, 255, 255], axis=-1)
# change the values of Alpha to 0 for all the white pixels
backtocolor[white, -1] = 0

red_img  = np.full(backtocolor.shape, (0,0,255), np.uint8)
fused_img  = cv2.addWeighted(backtocolor, 0.8, red_img, 0.2, 0)


## Skin texture masking 
skin = cv2.imread('skin/Skin_01_basecolorpink4.jpg')
skin = cv2.resize(skin, (100, 100), interpolation = cv2.INTER_NEAREST)
masked = cv2.bitwise_and(skin, skin, mask=cv2.bitwise_not(blur))
alpha = np.sum(masked, axis=-1) > 0

# Convert True/False to 0/255 and change type to "uint8" to match "na"
alpha = np.uint8(alpha * 255)

# Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
res = np.dstack((masked, alpha))


cv2.imwrite("cv/map1234bis.png", res)
cv2.imshow("Resized image", res)
cv2.waitKey(0)



#cv2.imwrite("cv/blur2otsu.png", blur)

#cv2.imshow("Resized image", backtocolor)
#cv2.waitKey(0)


# Convert a matrix of pressure value into an array of 32 x 32 value 0..1
#img_reverted= cv2.bitwise_not(img)
#new_img = np.round(img_reverted / 255.0 ,2)
#x_str = np.array_repr(new_img).replace('\n', '')
#x2=new_img.flatten()
#x_str = np.array_repr(x2).replace('\n', '')
