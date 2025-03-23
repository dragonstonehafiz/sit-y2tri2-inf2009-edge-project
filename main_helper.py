from helper.BoardInterface import BoardInterface
from helper.AudioInterface import AudioInterface
from helper.PiCameraInterface import PiCameraInterface
from helper.MQTT import MQTT_Publisher
from helper.utils import convert_frame_to_bytes

import os
import threading
from enum import Enum

CORE_ID_SERVO = 1
CORE_ID_MODEL = 2

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

def run_on_core(core_id: int, target_func: callable, *args, **kwargs):
    def wrapper():
        # Pin the thread to a specific core
        os.sched_setaffinity(0, {core_id})
        target_func(*args, **kwargs)
    
    thread = threading.Thread(target=wrapper)
    thread.start()
    return thread

# 
def record_audio_thread(global_data: dict):
    audio = AudioInterface()
    while global_data["is_running"]:
        if global_data["state"] != STATES.IDLE:
            global_data["most_recent_sound"], global_data["most_recent_sound_peak_amp"] = None, None
        else:
            global_data["most_recent_sound"], global_data["most_recent_sound_peak_amp"] = audio.record_audio(3)  # Record for 3 seconds

def handle_picam(global_data: dict):
    # Get the current frames cam image and send it (if needed)
    picam: PiCameraInterface = global_data["picam"]
    frame = picam.getFrame()
    global_data["curr_frame"] = frame
    # Send image to server
    mqtt_cam_feed: MQTT_Publisher = global_data["mqtt_cam_feed"]
    if mqtt_cam_feed is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_cam_feed.send(frame_bytes)

def scan_handle_x(board: BoardInterface, global_data: dict, servo_turn_rate_x=10, servo_turn_rate_y=15):
    # Turn servo x in either left or right
    # then check if the servo is at max/min
    # if it is, turn the y servo
    scan_dir_x = global_data["scan_dir_x"]
    if scan_dir_x:
        board.turn_servo_x(servo_turn_rate_x)

        if is_servo_out_of_bounds(board.get_servo_x(), x=True):
            scan_dir_x = not scan_dir_x
            scan_handle_y(board, global_data, servo_turn_rate=servo_turn_rate_y)
            
    elif not scan_dir_x:
        board.turn_servo_x(-servo_turn_rate_x)

        if is_servo_out_of_bounds(board.get_servo_x(), x=True):
            scan_dir_x = not scan_dir_x
            scan_handle_y(board, global_data, servo_turn_rate=servo_turn_rate_y)
    
    global_data["scan_dir_x"] = scan_dir_x

def scan_handle_y(board: BoardInterface, global_data: dict, servo_turn_rate = 15):
    scan_dir_y = global_data["scan_dir_y"]

    if scan_dir_y:
        board.turn_servo_y(servo_turn_rate)
        if is_servo_out_of_bounds(board.get_servo_y(), x=False):
            scan_dir_y = not scan_dir_y
    elif not scan_dir_y:
        board.turn_servo_y(-servo_turn_rate)
        if is_servo_out_of_bounds(board.get_servo_y(), x=False):
            scan_dir_y = not scan_dir_y

    global_data["scan_dir_y"] = scan_dir_y

def is_servo_out_of_bounds(angle: int, x: bool):
    if x:
        return angle >= 180 or angle <= 0
    else:
        return angle >= 180 or angle <= 0

