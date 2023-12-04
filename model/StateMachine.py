import numpy as np

from model.ObjectDetection import ObjectDetector
from model.ObjectTracking import ObjectTracker
from sensors import stepper
# from sensors import camera
from pyfirmata import Arduino



SENSOR_DELAY = 1
BASE_SURVEILLANCE_AMOUNT = 60
BASE_MAXIMUM_ANGLE_AMOUNT = 300
BASE_MINIMUM_ANGLE_AMOUNT = -120
CAMERA_SURVEILLANCE_AMOUNT = 40
CAMERA_MINIMUM_ANGLE_AMOUNT = 0
CAMERA_MAXIMUM_ANGLE_AMOUNT = 180


class StateMachine():
    def __init__(self):
        # sensors = self.initialize_sensors()
        # self.camera = sensors[0]
        # self.board = sensors[1]
        self.state = {"motion_state" : "surveillance","camera_angle":90, "base_angle":90, "camera_rotation_direction" : "CCW", "base_rotation_direction" : "CCW"}
        self.object_detection = ObjectDetector()
        self.object_tracker = ObjectTracker()
    # def initialize_sensors(self):
    #     picam  = camera.initialize_camera()
    #     picam.start()
    #     board = Arduino('/dev/ttyACM0')
    #     return [picam, board]
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






        
    
        


    
        

        


        