from model.ObjectDetection import ObjectDetector
import cv2
import numpy as np

frame = cv2.imread("./img_1.jpeg")
det = ObjectDetector()
x = det.get_combined_detections(frame)
print(x)