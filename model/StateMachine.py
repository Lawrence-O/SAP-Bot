import time
import cv2
from sensors import stepper
from sensors import camera
from PIL import Image
from pyfirmata import Arduino
from Net import ONNX_NET
import torch


SENSOR_DELAY = 1
BASE_SURVEILLANCE_AMOUNT = 60
BASE_MAXIMUM_ANGLE_AMOUNT = 300
BASE_MINIMUM_ANGLE_AMOUNT = -120
CAMERA_SURVEILLANCE_AMOUNT = 40
CAMERA_MINIMUM_ANGLE_AMOUNT = 0
CAMERA_MAXIMUM_ANGLE_AMOUNT = 180
ONNX_INPUT_IMAGE_SIZE = (128,128)
ONNX_DATA_PATH = "./bin/yolo_data.pickle"
ONNX_MODEL_PATH = "./bin/yolov8_sap.onnx"
MINIMUM_CLASS_SCORE = 0.25

class StateMachine():
    def __init__(self, cnn_path):
        sensors = self.initialize_sensors()
        self.camera = sensors[0]
        self.board = sensors[1]
        self.state = {"motion_state" : "surveillance","camera_angle":90, "base_angle":90, "camera_rotation_direction" : "CCW", "base_rotation_direction" : "CCW"}
        self.yolo_sap = ONNX_NET(ONNX_DATA_PATH,ONNX_MODEL_PATH)
    def initialize_sensors(self):
        picam  = camera.initialize_camera()
        picam.start()
        board = Arduino('/dev/ttyACM0')
        return [picam, board]
    def surveillance_base(self):
        if self.state["base_rotation_direction"] == "CCW" and self.state["base_angle"] <= BASE_MAXIMUM_ANGLE_AMOUNT:
            #Rotate CCW when angle is less than 300
            stepper.rotate_base_stepper(BASE_SURVEILLANCE_AMOUNT, self.state["base_rotation_direction"], self.board)
            self.state["base_angle"] += BASE_SURVEILLANCE_AMOUNT
        elif self.state["base_rotation_direction"] == "CW" and self.state["base_angle"] >= BASE_MINIMUM_ANGLE_AMOUNT:
            #Rotate CW; when angle is greater than 120
            stepper.rotate_base_stepper(BASE_SURVEILLANCE_AMOUNT, self.state["base_rotation_direction"], self.board)
            self.state["base_angle"] -= BASE_SURVEILLANCE_AMOUNT
        else:
            # We've reached one of the constraints; reset direction now
            self.state["base_rotation_direction"] = "CCW" if self.state["base_rotation_direction"] == "CW" else "CW"
    def surveillance_camera(self):
        if self.state["camera_rotation_direction"] == "CCW" and self.state["camera_angle"] <= CAMERA_MAXIMUM_ANGLE_AMOUNT:
            #Rotate CCW when angle is less than 300
            stepper.rotate_camera_stepper(CAMERA_SURVEILLANCE_AMOUNT, self.state["camera_rotation_direction"], self.board)
            self.state["camera_angle"] += CAMERA_SURVEILLANCE_AMOUNT
        elif self.state["camera_rotation_direction"] == "CW" and self.state["base_angle"] >= CAMERA_MINIMUM_ANGLE_AMOUNT:
            #Rotate CW; when angle is greater than 120
            stepper.rotate_camera_stepper(CAMERA_SURVEILLANCE_AMOUNT, self.state["camera_rotation_direction"], self.board)
            self.state["camera_angle"] -= CAMERA_SURVEILLANCE_AMOUNT
        else:
            # We've reached one of the constraints; reset direction now
            self.state["camera_rotation_direction"] = "CCW" if self.state["camera_rotation_direction"] == "CW" else "CW"
    def preprocess_frame(self,frame):
        image = Image.fromarray(frame)
        image = cv2.resize(image,ONNX_INPUT_IMAGE_SIZE)
        return cv2.dnn.blobFromImage(image, 1/255.0, ONNX_INPUT_IMAGE_SIZE, swapRB=True)
    def process_frame(self,frame):
        blob = self.preprocess_frame(frame)
        net = self.yolo_sap.get_onnx_net()
        predictions = net.forward()
        return predictions[0]
    def unwrap_detections(self,frame,cnn_output):
        class_ids, confidences, bboxes = [],[],[]
        
    
        


    
        

        


        