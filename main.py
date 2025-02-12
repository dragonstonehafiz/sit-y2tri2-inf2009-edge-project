from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.StateHandler import stateIdle, stateScan, stateTracking, STATES


if __name__ == "__main__":
    board = RaspberryPiZero2()
    currState = STATES.IDLE
    
    while True:
        if currState == STATES.IDLE:
            currState = stateIdle()
        elif currState == STATES.SCAN:
            currState = stateScan(board)
        elif currState == STATES.TRACKING:
            currState = stateTracking(board)
        elif currState == STATES.QUIT:
            break
    
    board.cleanup()