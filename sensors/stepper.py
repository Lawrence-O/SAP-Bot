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
    steps_per_revolution = 200*32
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
    steps_per_revolution = 200*32
    steps = 0
    while steps < steps_per_revolution*(angle/360.0):
        board.digital[pitchStepPin].write(1)
        time.sleep(0.0015)
        board.digital[pitchStepPin].write(0)
        time.sleep(0.0015)
        steps += 1

    
def track_target_base(x, camera_center_x, board):
    angle_per_unit = 33/camera_center_x
    angle = (x-camera_center_x)*angle_per_unit
    if angle <= 0:
        rotate_base_stepper(abs(angle), 'CCW', board)
        return (abs(angle), 'CW')
    else:
        rotate_base_stepper(abs(angle), 'CW', board)
        return (abs(angle), 'CCW')

def track_target_camera(y, camera_center_y, board):
    angle_per_unit = 20/camera_center_y
    angle = (y-camera_center_y)*angle_per_unit
    if angle <= 0:
        rotate_camera_stepper(abs(angle), 'CCW', board)
        return (abs(angle), 'CW')
    else:
        rotate_camera_stepper(abs(angle), 'CW', board)
        return (abs(angle), 'CCW')