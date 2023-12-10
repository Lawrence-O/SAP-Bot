from model.ObjectDetection import ObjectDetector
import cv2
import numpy as np
import heapq

minHeap = [(-0.02,[-1,0,952,974])]
heapq.heapify(minHeap)

print(minHeap)