from pyfirmata import Arduino, util
import time

pumpPin = 3

def shoot_liquid(board):
    board.digital[pumpPin].write(1)
    time.sleep(1.2)
    board.digital[pumpPin].write(0)