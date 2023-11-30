from pyfirmata import Arrduinno, util

sensorPin = 0
ledPin1 = 9
ledPin2 = 10
ledPin3 = 11
ledPin4 = 12

def check_liquid_level(board):
    
    sensorRead = board.analog_read(sensorPin)
    board.digital[ledPin1].write(0)
    board.digital[ledPin2].write(0)
    board.digital[ledPin3].write(0)
    board.digital[ledPin4].write(0)
    if sensorRead < 840:
        board.digital[ledPin1].write(1)
        return "EMPTY"
    elif sensorRead < 870:
        board.digital[ledPin1].write(1)
        return "LOW"
    elif sensorRead < 880:
        board.digital[ledPin1].write(1)
        board.digital[ledPin2].write(1)
        return "MEDIUM"
    elif sensorRead < 930:
        board.digital[ledPin1].write(1)
        board.digital[ledPin2].write(1)
        board.digital[ledPin3].write(1)
        return "HIGH"
    else:
        board.digital[ledPin1].write(1)
        board.digital[ledPin2].write(1)
        board.digital[ledPin3].write(1)
        board.digital[ledPin4].write(1)
        return "FULL"


