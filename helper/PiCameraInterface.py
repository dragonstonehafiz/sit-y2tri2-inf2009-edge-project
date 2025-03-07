from picamera2 import Picamera2
import cv2

class PiCameraInterface:
    _camera: Picamera2
    _cameraSize: tuple[int, int]
    _cameraCenter: tuple[int, int]
    
    def __init__(self, _cameraSize: tuple = (640, 640)):
        self._camera = Picamera2()
        self._cameraSize = _cameraSize
        self._cameraCenter = ((int)(_cameraSize[0] / 2), (int)(_cameraSize[1] / 2))
    
    def start(self):
        config = self._camera.create_preview_configuration(main={"size": self._cameraSize})
        self._camera.configure(config)
        self._camera.start()
    
    def getFrame(self):
        frame = self._camera.capture_array()
        # since the camera is actually upside down on the gimbal, we have to flip the frame on the y-axis
        frame = cv2.flip(frame, 0)
        return frame
    
    def close(self):
        self._camera.close()
    
    def getCenter(self):
        return self._cameraCenter
    
    def getSize(self):
        return self._cameraSize