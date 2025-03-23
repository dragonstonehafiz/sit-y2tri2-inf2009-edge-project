import numpy as np
import cv2

def convert_frame_to_bytes(frame) -> bytes:
    """convert image data to bytes"""
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def convert_bytes_to_frame(bytes):
    """convert bytes to image data"""
    np_arr = np.frombuffer(bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

def get_closest_coords(coords: tuple[int, int], object_coords: list[tuple[int, int]]):
    """
    Gets a list of object coords and finds closest to a given coord
    :param coord: coord to compare against
    :param objectCoords: list of objects to compare against
    """
    x, y = coords
    closest_coords = (9999, 9999)

    closest_dist_squared = 999 ** 2
    for obj_coord in object_coords:
        obj_x, obj_y = obj_coord
        dist_squared = (obj_x - x) ** 2 + (obj_y - y) ** 2
        if dist_squared < closest_dist_squared:
            closest_dist_squared = dist_squared
            closest_coords = obj_coord

    return closest_coords

def normalize_displacement(displacement: tuple[int, int], frameSize: tuple[int, int]) -> tuple[int, int]:
    """
    Normalizes the displacement of an object from the center of the screen.
    """
    xDisplacement, yDisplacement = displacement
    xDisplacement = (int) (xDisplacement / (frameSize[0] / 16))
    yDisplacement = (int) (yDisplacement / (frameSize[1] / 16))
    return (xDisplacement, yDisplacement)

def get_object_displacement(objectCenter, screenCenter, screenSize) -> tuple[int, int]:
    """
    Returns the displacement of an object from the center of the screen.
    """
    xDisplacement = objectCenter[0] - screenCenter[0]
    yDisplacement = objectCenter[1] - screenCenter[1]
    return normalize_displacement((xDisplacement, yDisplacement), screenSize)
