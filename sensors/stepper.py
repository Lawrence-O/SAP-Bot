from pyfirmata import Arduino, util
import time

pitchDirPin = 5
pitchStepPin = 4
yawDirPin = 7
yawStepPin = 6




def rotate_base_stepper(angle, direction, board):
    if direction == 'CCW':
        board.digital[yawDirPin].write(0)
    else:
        board.digital[yawDirPin].write(1)
    steps_per_revolution = 200*8
    steps = 0
    while steps < steps_per_revolution*(angle/360.0):
        board.digital[yawStepPin].write(1)
        time.sleep(0.0015)
        board.digital[yawStepPin].write(0)
        time.sleep(0.0015)
        steps += 1

def rotate_camera_stepper(angle,direction,board):
    if direction == 'CCW':
        board.digital[pitchDirPin].write(0)
    else:
        board.digital[pitchDirPin].write(1)
    steps_per_revolution = 200*8
    steps = 0
    while steps < steps_per_revolution*(angle/360.0):
        board.digital[pitchStepPin].write(1)
        time.sleep(0.0015)
        board.digital[pitchStepPin].write(0)
        time.sleep(0.0015)
        steps += 1

def track_base_stepper(x, cam_center_x, board):
    angle_per_unit = 30/cam_center_x
    angle = (x-cam_center_x)*angle_per_unit
    if (angle < 0):
        rotate_base_stepper(angle, 'CCW', board)
    else:
        rotate_base_stepper(angle, 'CW', board)
    return angle

def track_camera_stepper(y, cam_center_y, board):
    angle_per_unit = 20/cam_center_y
    angle = (y-cam_center_y)*angle_per_unit
    if (angle < 0):
        rotate_camera_stepper(angle, 'CCW', board)
    else:
        rotate_base_stepper(angle, 'CW', board)
    return angle
        