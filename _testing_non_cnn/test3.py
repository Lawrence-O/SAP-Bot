import cv2 
import numpy as np 
from IPython.display import Image, display 
from matplotlib import pyplot as plt


# Plot the image 
def imshow(img, ax=None): 
	if ax is None: 
		ret, encoded = cv2.imencode(".jpg", img) 
		display(Image(encoded)) 
	else: 
		ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) 
		ax.axis('off') 

#Image loading 
img = cv2.imread("10ft.jpg") 
# img = cv2.GaussianBlur(img, (7,7),0)

#image grayscale conversion 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
# Show image 
imshow(img)

#Threshold Processing 
ret, bin_img = cv2.threshold(gray, 
							0, 255, 
							cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) 
imshow(bin_img)


# noise removal 
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13)) 
bin_img = cv2.morphologyEx(bin_img,  
                           cv2.MORPH_OPEN, 
                           kernel, 
                           iterations=2) 
bin_img = cv2.dilate(bin_img,kernel=kernel,iterations=1)
imshow(bin_img) 

# Create subplots with 1 row and 2 columns 
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8)) 
# sure background area 
sure_bg = cv2.dilate(bin_img, kernel, iterations=3) 
imshow(sure_bg, axes[0,0]) 
axes[0, 0].set_title('Sure Background') 
  
# Distance transform 
dist = cv2.distanceTransform(bin_img, cv2.DIST_L1, 5) 
imshow(dist, axes[0,1]) 
axes[0, 1].set_title('Distance Transform') 
  
#foreground area 
ret, sure_fg = cv2.threshold(dist, 0.1 * dist.max(), 255, cv2.THRESH_BINARY) 
sure_fg = sure_fg.astype(np.uint8)   
imshow(sure_fg, axes[1,0]) 
axes[1, 0].set_title('Sure Foreground') 
  
# unknown area 
unknown = cv2.subtract(sure_bg, sure_fg) 
imshow(unknown, axes[1,1]) 
axes[1, 1].set_title('Unknown') 
  
plt.show()