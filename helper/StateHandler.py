from enum import Enum
from RaspberryPiZero2 import RaspberryPiZero2
import time

#1 鳥を待つ。鳥が鳴くと、次のモードに変更する
#2 鳥を探す。カメラは回して、x-axisだけ動く180度でな
#3 見つかった鳥を追跡する。カメラはその鳥を画面で真ん中にする

# If time since last bird seen is too large, go back to idle mode
lastBirdSeenTime = time.time()

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3
    
def stateIdle() -> int:
    """
    Stays in this function until a sound is detected.
    """
    soundDetected = True # Placeholder for sound detection
    if soundDetected:
        return STATES.SCAN
    else:
        return STATES.IDLE
    
def stateScan(board: RaspberryPiZero2) -> int:
    """
    Rotates the camera in the x axis until it sees a bird. Then it changes to the next state.
    """
    if board.getScanDir():
        board.turnServoX(1)
        if board.getServoXAngle() >= 180:
            board.toggleScanDir()
    else:
        board.turnServoY(-1)
        if board.getServoXAngle() <= 0:
            board.toggleScanDir()
            
    frame = board.getCamFrame()
    birdDetected = False # Placeholder for bird detection
    if birdDetected:
        
        return STATES.TRACKING
        
def stateTracking(board: RaspberryPiZero2) -> int:
    """
    Tracks the bird in the center of the screen.
    """
    frame = board.getCamFrame()
    now = time.time()
    birdSeen = True # object detection code comes here
    if birdSeen:
        # To position the camera, we will be using the center of the image as the origin
        # We will then get the position of the detected bird relative to origin and turn the servos accordingly
        # Example, if the bird is at position (50, 0), we will turn the x-servo to the right (speed/turn rate is not important, we only care about direction). Conversely, if the bird is at position (-50, 0), we will turn x-servo to the left. 
        birdPos = (240, 240)
        xDisplacement = birdPos[0] - board.getCamCenter()[0]
        yDisplacement = birdPos[1] - board.getCamCenter()[1]
        
        # We're only turning one servo at a time
        if abs(xDisplacement) > abs(yDisplacement):
            if xDisplacement > 0:
                board.turnServoX(5)
            else:
                board.turnServoX(-5)
        else:
            if yDisplacement > 0:
                board.turnServoY(5)
            else:
                board.turnServoY(-5)
        
        # Update last seen time  
        lastBirdSeenTime = now
    else:
        # If no bird is seed for more than 15 seconds, go back to idle mode
        if now - lastBirdSeenTime > 15:
            return STATES.IDLE