
from model import StateMachine

CNN_PATH = ""

stateMachine = StateMachine.StateMachine(cnn_data_path=CNN_PATH)
while True:
    stateMachine.surveillance_one_step()