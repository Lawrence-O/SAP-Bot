from picamera2 import Picamera2, Preview
from libcamera import Transform
import time


def initialize_camera():
    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL)
    preview_config = picam2.create_preview_configuration(transform=Transform(hflip=1, vflip=1))
    picam2.configure(preview_config)
    return picam2
 
# raspberrypi = initialize_camera()
# raspberrypi.start()
# time.sleep(0.1)
# while True:
#     frame = raspberrypi.capture_array()
#     print(frame.size)