from pyfirmata import Arduino, util
import time



def rotate_stepper(angle, direction, board):
    if direction == 'CCW':
        board.digital[2].write(0)
    else:
        board.digital[2].write(1)
    steps_per_revolution = 200*8
    steps = 0
    while steps < steps_per_revolution*(angle/360.0):
        board.digital[3].write(1)
        time.sleep(0.0015)
        board.digital[3].write(0)
        time.sleep(0.0015)
        steps += 1

