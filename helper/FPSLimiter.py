import time

class FPSLimiter:
    _fps: int
    """The target refresh rate for the system (in Hz).
    """
    _framePeriod: float
    """How long a single frame lasts (in seconds).
    """
    _frameStartTime: float
    """The time the current frame was rendered.
    """
    _deltaTime: float
    """The time taken to render the current frame.
    """
    
    def __init__(self, targetRefreshRate: int = 24):
        print("Initializing RefreshRateLimiter")
        self._fps = targetRefreshRate
        self._framePeriod = 1.0 / targetRefreshRate
        
    def startFrame(self):
        """Starts a new frame.
        """
        self._frameStartTime = time.time()
        
    def endFrame(self):
        """Limits the refresh rate of the system to the target refresh rate.
        """
        # Find the time taken to render the frame
        frameEndTime = time.time()
        elapsedTime = frameEndTime - self._frameStartTime
        # If that time is less than the target frame period, sleep for the difference
        if elapsedTime < self._framePeriod:
            time.sleep(self._framePeriod - elapsedTime)
        frameEndTime = time.time()
        self._deltaTime = frameEndTime - self._frameStartTime
        
    def getDeltaTime(self):
        """Returns the time taken to render the current frame.
        """
        return self._deltaTime
        
if __name__ == "__main__":
    rrl = FPSLimiter(24)
    frameCount = 0
    startTime = time.time()
    elapsedTime = 0
    while True:
        now = time.time()
        rrl.startFrame()
        rrl.endFrame()()
        elapsedTime += rrl.getDeltaTime()
        print(f"{elapsedTime:.2f}")
        if (now - startTime) > 3:
            break