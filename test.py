import cv2
import numpy as np

def detect_red(frame):
    # Convert BGR to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define range of red color in HSV
    lower_red = np.array([0, 120, 70])  # Lower HSV values for red
    upper_red = np.array([10, 255, 255])  # Upper HSV values for red

    # Define a mask using inRange function
    red_mask1 = cv2.inRange(hsv_frame, lower_red, upper_red)

    # Define range for the second shade of red
    lower_red = np.array([170, 120, 70])  # Lower HSV values for red
    upper_red = np.array([180, 255, 255])  # Upper HSV values for red

    # Define a second mask using inRange function
    red_mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)

    # Combine masks to encompass a broader range of red hues
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Bitwise-AND mask and original image
    red_res = cv2.bitwise_and(frame, frame, mask=red_mask)

    return red_mask, red_res

frame = cv2.imread("./red_test.jpg")
red_mask, red_result = detect_red(frame)

contours,_ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)
for cnt in contours:
    (x, y, w, h) = cv2.boundingRect(cnt)
    x_medium = int((x + x + w) / 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    break

# Display the frames
cv2.imshow('Frame', frame)
cv2.imshow('Red Mask', red_mask)
cv2.imshow('Red Detected', red_result)
cv2.waitKey(0)