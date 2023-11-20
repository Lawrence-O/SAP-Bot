from pyfirmata import Arduino, util
import time

if __name__ == '__main__':

    board = Arduino('/dev/ttyACM0')

    print('Communication successfully started')

    board.digital[2].write(0) # Direction Pin, 1 == CW, 0 == CCW

    try:
        
        while True:
            board.digital[3].write(1)
            time.sleep(0.0005)
            board.digital[3].write(0)
            time.sleep(0.0005)
    except KeyboardInterrupt:
        board.exit()
    
    
        