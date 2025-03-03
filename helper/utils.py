import numpy as np
import cv2

def convert_frame_to_bytes(frame) -> bytes:
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def convert_bytes_to_frame(bytes):
    np_arr = np.frombuffer(bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)