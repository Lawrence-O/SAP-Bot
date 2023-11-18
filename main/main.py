import time
from sensors import camera
from model import StateMachine

SENSOR_DELAY = 1

picam  = camera.initialize_camera()
picam.start()
time.sleep(SENSOR_DELAY)

def initialize_cnn(path):
    

def process_frame(frame):
    pass

while True:
    frame = picam.capture_array()
    process_frame(frame)