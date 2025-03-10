import numpy as np
import cv2
import serial.tools.list_ports

def convert_frame_to_bytes(frame) -> bytes:
    """convert image data to bytes"""
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def convert_bytes_to_frame(bytes):
    """convert bytes to image data"""
    np_arr = np.frombuffer(bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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

def list_serial_ports():
    """Lists available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")