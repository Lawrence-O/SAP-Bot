import time
import cv2
from sensors import camera
from model import ConvNet
from collections import defaultdict
from PIL import Image

SENSOR_DELAY = 1

class state_machine():
    def __init__(self, cnn_data_path):
        sensors = self.initialize_sensors()
        self.camera = sensors[0]
        self.onnx_net = ConvNet.ONNX_NET(cnn_data_path)
        self.opencv_net = self.onnx_net.get_onnx_net()
        # self.state = defaultdict(lambda)
    def initialize_sensors(self):
        picam  = camera.initialize_camera()
        picam.start()
        return [picam]
    def get_state(self):
        pass
    def update_state(self, new_state):
        pass
    def process_frame(self,frame):
        frame = Image.fromarray(frame)
        frame = frame.resize((64,64))
        


    
        

        


        