from picamera2 import Picamera2, Preview
from libcamera import Transform, controls
import time


def initialize_camera():
    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL)
    main_config = {"size":(1280,720)}
    preview_config = picam2.create_preview_configuration(main=main_config,transform=Transform(hflip=1, vflip=1),)
    picam2.configure(preview_config)
    # picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 30.0})
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
    # success = picam2.autofocus_cycle()
    return picam2
 
# raspberrypi = initialize_camera()
# raspberrypi.start()
# time.sleep(0.1)
# while True:
#     frame = raspberrypi.capture_array()
#     print(frame.size)