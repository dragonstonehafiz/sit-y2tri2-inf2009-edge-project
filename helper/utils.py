import numpy as np
import cv2

def convert_frame_to_bytes(frame) -> bytes:
    """convert image data to bytes"""
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def convert_bytes_to_frame(bytes):
    """convert bytes to image data"""
    np_arr = np.frombuffer(bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

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