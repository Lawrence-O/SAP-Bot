import cv2
import cv2.legacy as legacy
import numpy as np
from PIL import Image


from model import Net
# from sensors import camera
from imutils.object_detection import non_max_suppression
from collections import defaultdict


SAP_INPUT_IMAGE_SIZE = (128,128)
YOLO_INPUT_IMAGE_SIZE = (640,640)
SAP_ONNX_DATA_PATH = "./bin/sap_yolo_data.pickle"
SAP_ONNX_MODEL_PATH = "./bin/yolov8_sap.onnx"
ORG_ONNX_DATA_PATH = "./bin/org_yolo_data.pickle"
ORG_ONNX_MODEL_PATH = "./bin/yolov8_org.onnx"
MINIMUM_DETECTION_SCORE = 0.3
MINIMUM_CLASS_SCORE = 0.8
SAP_DETECTION_WEIGHT = 0.6
CLASS_ID_SAP_OFFSET = 80

class ObjectDetector():
    def __init__(self):
        self.yolo_sap = Net.ONNX_NET(SAP_ONNX_DATA_PATH,SAP_ONNX_MODEL_PATH)
        self.yolo_org = Net.ONNX_NET(ORG_ONNX_DATA_PATH,ORG_ONNX_MODEL_PATH)
        self.tracker = legacy.TrackerMOSSE().create()
    def preprocess_frame(self,frame,resize_size):
        return cv2.dnn.blobFromImage(frame, 1/255.0,resize_size,swapRB=True,crop=False)
    def process_frame(self,blob,model):
        net = model
        net.setInput(blob)
        predictions = net.forward()
        return  predictions.transpose((0, 2, 1))
    def unwrap_detections(self,frame,cnn_output,resize_size,class_id_offset=0):
        labels = dict()
        image_height, image_width, _ = frame.shape
        x_factor = image_width / resize_size[0]
        y_factor = image_height / resize_size[1]
        rows = cnn_output[0].shape[0]
        for i in range(rows):
            row = cnn_output[0][i]
            conf = row[4]
            classes_score = row[4:]
            _,_,_, max_idx = cv2.minMaxLoc(classes_score)
            class_id = max_idx[1]
            if (classes_score[class_id] > MINIMUM_CLASS_SCORE):
                # confs.append(conf)
                label = int(class_id) + class_id_offset          
                #extract boxes
                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                # print(conf if label == 81 else "none",classes_score[class_id] if label == 81 else "none",)
                labels[label] = labels.get(label, []) + [(box,conf)]
        return  labels
    def apply_nms(self, detections):
        #Concatinate Matrixes to only 1 (each row is an object)
        final_detections = dict()
        for label in detections:
            bboxes = np.array([b[0] for b in detections[label]])
            probs = np.array([p[1] for p in detections[label]])
            converted_boxes = [(box[0], box[1], box[0] + box[2], box[1] + box[3]) for box in bboxes]
            boxes = non_max_suppression(np.array(converted_boxes), probs,overlapThresh=0.8)
            final_detections[label] = boxes
        return final_detections
    def get_pest_detections(self,frame):
        blob = self.preprocess_frame(frame,SAP_INPUT_IMAGE_SIZE)
        output = self.process_frame(blob,model=self.yolo_sap.get_onnx_net())
        labels = self.unwrap_detections(frame, output,SAP_INPUT_IMAGE_SIZE,CLASS_ID_SAP_OFFSET)
        return labels
    def get_object_detections(self,frame):
        blob = self.preprocess_frame(frame,YOLO_INPUT_IMAGE_SIZE)
        output = self.process_frame(blob,model=self.yolo_org.get_onnx_net())
        labels = self.unwrap_detections(frame, output,YOLO_INPUT_IMAGE_SIZE)
        return labels
    def get_combined_detections(self,frame):
        pest_detections = self.get_pest_detections(frame)
        object_detections = self.get_object_detections(frame)
        return self.apply_nms(pest_detections | object_detections)
    