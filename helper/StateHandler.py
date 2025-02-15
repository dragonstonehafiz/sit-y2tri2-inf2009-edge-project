from enum import Enum
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.FaceDetector import FaceDetector
import time

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

class StateHandler:
    # Logic specific variables
    _faceDetector = FaceDetector() # This is just a temp thing to test turning the servos
    _currentState = STATES.IDLE
    _lastBirdSeenTime: float = time.time()
    
    # Board Specific Variables
    _scanDir: bool = True # True means turn right, False means turn left
    _board = RaspberryPiZero2()
    
    def __init__(self):
        pass
    
    def setState(self, state: STATES):
        self._currentState = state
        if state == STATES.IDLE:
            self._board.setServoX(90)
            self._board.setServoY(90)
        elif state == STATES.SCAN:
            self._board.setServoX(90)
            self._board.setServoY(90)
            self._scanDir = True
        elif state == STATES.TRACKING:
            self._lastBirdSeenTime = time.time()
        elif state == STATES.QUIT:
            self._board.cleanup()
            
    def mainLoop(self):
        while True:
            try:
                if self._currentState == STATES.IDLE:
                    self._stateIdle()
                elif self._currentState == STATES.SCAN:
                    self._stateScan()
                elif self._currentState == STATES.TRACKING:
                    self._stateTracking()
                else:
                    print("No State. Quitting")
                    break
            except KeyboardInterrupt as e:
                print("Exiting...")
                break
            except Exception as e:
                print(f"Exception: {e}")
                break
        
        # Reset board values
        self._board.cleanup()
            
    def _stateIdle(self):
        """
        Stays in this function until a sound is detected.
        """
        soundDetected = True # Placeholder for sound detection
        if soundDetected:
            self.setState(STATES.SCAN)
        else:
            self.setState(STATES.IDLE)
            
    def _stateScan(self):
        """
        Rotates the camera in the x axis until it sees a bird. Then it changes to the next state.
        """
        board = self._board
        scanDir = self._scanDir
        
        # If the board reaches it's maximum/minimum angle, change direction
        if scanDir:
            board.turnServoX(1)
            if board.getServoXAngle() >= 180:
                scanDir = False
        else:
            board.turnServoX(-1)
            if board.getServoXAngle() <= 0:
                scanDir = True
        
        self._scanDir = scanDir
        
        frame = board.getCamFrame()
        faces = self._faceDetector.detect(frame)
        if len(faces) > 0:
            self.setState(STATES.TRACKING)
            
    def _stateTracking(self):
        """
        Tracks the bird in the center of the screen.
        """
        board = self._board
        frame = board.getCamFrame()
        now = time.time()
        faces = self._faceDetector.detect(frame)
        birdSeen = len(faces) > 0
        if birdSeen:
            # To position the camera, we will be using the center of the image as the origin
            # We will then get the position of the detected bird relative to origin and turn the servos accordingly
            # Example, if the bird is at position (50, 0), we will turn the x-servo to the right (speed/turn rate is not important, we only care about direction). Conversely, if the bird is at position (-50, 0), we will turn x-servo to the left. 
            
            (x, y, w, h) = faces[0]             # just track the first face
            birdPos = (x + w / 2, y + h / 2)    # Get the center of the face
            xDisplacement = birdPos[0] - board.getCamCenter()[0]
            yDisplacement = birdPos[1] - board.getCamCenter()[1]
            
            # We're only turning one servo at a time
            if abs(xDisplacement) > abs(yDisplacement):
                if xDisplacement > 0:
                    board.turnServoX(1)
                else:
                    board.turnServoX(-1)
            else:
                if yDisplacement > 0:
                    board.turnServoY(1)
                else:
                    board.turnServoY(-1)
            
            # Update last seen time  
            self._lastBirdSeenTime = now
        else:
            # If no bird is seed for more than 15 seconds, go back to idle mode
            if now - self._lastBirdSeenTime > 15:
                self.setState(STATES.IDLE)
    