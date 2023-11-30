import cv2
import numpy as np

# Load image
image = cv2.imread("5ft.jpg")
image = cv2.resize(image, (1024,1024))

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (7, 7), 0)

# Adaptive thresholding
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Find contours in the binary image
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Extract centroids of the contours
centers = []
for contour in contours:
    # Calculate the centroid of the contour
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centers.append((cX, cY))

# Draw the contours on the original image
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

# Draw the centers on the original image
for center in centers:
    cv2.circle(image, center, 5, (0, 0, 255), -1)

# Display the original image with contours and centers
cv2.imshow("Contours and Centers", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
