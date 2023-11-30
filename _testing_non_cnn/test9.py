import cv2
import numpy as np

# Read the image
image = cv2.imread("testpic2.jpg")
image = cv2.resize(image, (1024,1024))

# Create a SLIC superpixel object
slic = cv2.ximgproc.createSuperpixelSLIC(image, algorithm=cv2.ximgproc.SLICO, region_size=10)
slic.iterate(10)

# Get superpixel labels
labels = slic.getLabels()

# Create a mask for superpixels
mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)

# Assign a value to each superpixel region
for label in range(slic.getNumberOfSuperpixels()):
    mask[labels == label] = label

# Convert the mask to a binary image
mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]

# Apply the connected components to convert the mask to the marker image
markers, num_markers = cv2.connectedComponents(mask)

# Convert markers to 32-bit signed integers
markers = np.int32(markers)

markers = cv2.UMat(markers)

# Apply watershed segmentation
markers = cv2.watershed(cv2.convertScaleAbs(image), markers)

# Mark segmented regions on the original image
image[markers == -1] = [0, 0, 255]  # Mark watershed boundaries in red

# Display the result
cv2.imshow('Segmentation with Superpixels and Watershed', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
