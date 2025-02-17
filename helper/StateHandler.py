from enum import Enum
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.FaceDetector import FaceDetector
from helper.RefreshRateLimiter import RefreshRateLimiter
import time

def normalizeDisplacement(displacement: tuple[int, int], frameSize: tuple[int, int]) -> tuple[int, int]:
    """
    Normalizes the displacement of an object from the center of the screen.
    """
    xDisplacement, yDisplacement = displacement
    xDisplacement = (int) (xDisplacement / (frameSize[0] / 10))
    yDisplacement = (int) (yDisplacement / (frameSize[1] / 10))
    return (xDisplacement, yDisplacement)

def getObjectDisplacement(objectCenter, screenCenter, screenSize) -> tuple[int, int]:
    """
    Returns the displacement of an object from the center of the screen.
    """
    xDisplacement = objectCenter[0] - screenCenter[0]
    yDisplacement = objectCenter[1] - screenCenter[1]
    return normalizeDisplacement((xDisplacement, yDisplacement), screenSize)

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
    
    # Variable to control frame rate of camera
    _rrl: RefreshRateLimiter = RefreshRateLimiter(30)
    
    # Board Specific Variables
    _scanDir: bool = True # True means turn right, False means turn left
    _board = RaspberryPiZero2(debug=False)
    
    def __init__(self):
        pass
    
    def setState(self, state: STATES):
        self._currentState = state
        print(state)
        if state == STATES.IDLE:
            self._board.setServoX(90)
            self._board.setServoY(90)
        elif state == STATES.SCAN:
            self._board.setLaser(False)
            self._board.setServoX(90)
            self._board.setServoY(90)
            self._scanDir = True
        elif state == STATES.TRACKING:
            self._board.setLaser(True)
            self._lastBirdSeenTime = time.time()
        elif state == STATES.QUIT:
            self._board.cleanup()
            
    def main(self):
        """
        Main loop for the state machine
        """
        while True:
            # self._rrl.startFrame()
            
            continueLoop = self._mainloop()
            if not continueLoop:
                break
            
            # self._rrl.limit()
        
    def _mainloop(self) -> bool:
        """
        Returns true if the loop should continue, false if it should exit
        """
        try:
            if self._currentState == STATES.IDLE:
                self._stateIdle()
            elif self._currentState == STATES.SCAN:
                self._stateScan()
            elif self._currentState == STATES.TRACKING:
                self._stateTracking()
            else:
                print("No State. Quitting")
                return False
        except KeyboardInterrupt as e:
            print("Exiting...")
            return False
        except Exception as e:
            print(f"Exception: {e}")
            return False

        return True
              
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
            board.turnServoX(3)
            if board.getServoXAngle() >= 180:
                scanDir = False
        else:
            board.turnServoX(-3)
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
        face = self._faceDetector.detectClosestFace(frame, board.getCamCenter())
        birdSeen = face is not None
        if birdSeen:
            # To position the camera, we will be using the center of the image as the origin
            # We will then get the position of the detected bird relative to origin and turn the servos accordingly
            # Example, if the bird is at position (50, 0), we will turn the x-servo to the right (speed/turn rate is not important, we only care about direction). Conversely, if the bird is at position (-50, 0), we will turn x-servo to the left. 
            
            xDisplacement, yDisplacement = getObjectDisplacement(face, board.getCamCenter(), board.getCamSize())
            # We have to invert the y axis because the coordinate system is from top to bottom rather than bottom to top
            yDisplacement = -yDisplacement

            # print(f"xDisplacement:{xDisplacement}, yDisplacement:{yDisplacement}")
            if xDisplacement != 0:
                board.turnServoX(xDisplacement)
            
            # if yDisplacement != 0:
            #     board.turnServoY(yDisplacement)
            
            print(f"{self._board.getServoXAngle()},{xDisplacement}")
            # print(f"{self._board.getServoYAngle()},{yDisplacement}")
            # Update last seen time  
            self._lastBirdSeenTime = now
        else:
            # If no bird is seed for more than 7 seconds, go back to idle mode
            if now - self._lastBirdSeenTime > 7:
                self.setState(STATES.QUIT)
    
