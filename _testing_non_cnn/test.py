import cv2
import numpy as np

# Load image
image = cv2.imread("5ft.jpg")
image = cv2.resize(image, (1024,1024))
# image = cv2.GaussianBlur(image, (7,7),0)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# cv2.imshow("Segmented Image (Smaller)", thresh)
# cv2.waitKey(0)

# Noise removal using morphological operations
kernel = np.ones((7, 7), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

# cv2.imshow("Segmented Image (Smaller)", opening)
# cv2.waitKey(0)

# Sure background area
sure_bg = cv2.dilate(opening, kernel, iterations=3)

# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)

cv2.imshow("Segmented Image (Smaller)", unknown)
cv2.waitKey(0)

# Marker labelling
_, markers = cv2.connectedComponents(sure_fg)



# Add 1 to all labels so that sure background is not 0, but 1
markers = markers + 1


# Mark the region of unknown with 0
markers[unknown == 255] = 0

cv2.imshow("Segmented Image (Smaller)", cv2.applyColorMap((markers.astype(np.uint8) * 10) % 255,cv2.COLORMAP_JET))
cv2.waitKey(0)

# Apply watershed algorithm
markers = cv2.watershed(image, markers)


cv2.imshow("Segmented Image (Smaller)", cv2.applyColorMap((markers.astype(np.uint8) * 10) % 255,cv2.COLORMAP_JET))
cv2.waitKey(0)

# Outline the segmented regions with contours
image[markers == -1] = [0, 0, 255]  # Mark watershed boundaries in red


# Display the results in a smaller window
cv2.imshow("Segmented Image (Smaller)", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
