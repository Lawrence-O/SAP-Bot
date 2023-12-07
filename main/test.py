import stepper
import pump
import force_sensor
import time

from pyfirmata import Arduino, util

# pitchDirPin = 5
# pitchStepPin = 4
# yawDirPin = 7
# yawStepPin = 6

board = Arduino('/dev/ttyACM0')
print("Communication has started")

while True:
    # pump.shoot_liquid(board)
    # force_sensor.check_liquid_level(board)
    stepper.rotate_base_stepper(60, 'CW', board)
    stepper.rotate_camera_stepper(45, 'CCW', board)
    stepper.rotate_base_stepper(60, 'CCW', board)
    stepper.rotate_camera_stepper(45, 'CW', board)
    # time.sleep(5)
    
