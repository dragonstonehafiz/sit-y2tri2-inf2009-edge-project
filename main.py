from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.StateHandler import stateIdle, stateScan, stateTracking, STATES


if __name__ == "__main__":
    board = RaspberryPiZero2()
    currState = STATES.IDLE
    print(currState)
    
    while True:
        #  print(currState)
        if currState == STATES.IDLE:
            currState = stateIdle()
        elif currState == STATES.SCAN:
            currState = stateScan(board)
        elif currState == STATES.TRACKING:
            currState = stateTracking(board)
        elif currState == STATES.QUIT:
            break
        else:
            print("No State. Quitting")
            break

        try:
           pass
        except Exception as e:
           print(f"Exception: {e}")
           break
    
    board.cleanup()
