from helper.BoardInterface import BoardInterface
from helper.AudioInterface import AudioInterface

from enum import Enum

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

# 
def record_audio_thread(global_data: dict):
    audio = AudioInterface()
    while global_data["is_running"]:
        if global_data["state"] != STATES.IDLE:
            global_data["most_recent_sound"], global_data["most_recent_sound_peak_amp"] = None, None
        else:
            global_data["most_recent_sound"], global_data["most_recent_sound_peak_amp"] = audio.record_audio(3)  # Record for 3 seconds
            


def scan_handle_x(board: BoardInterface, global_data: dict):
    # Turn servo x in either left or right
    # then check if the servo is at max/min
    # if it is, turn the y servo
    scan_dir_x = global_data["scan_dir_x"]
    if scan_dir_x:
        board.turn_servo_x(3)

        if is_servo_out_of_bounds(board.get_servo_x(), x=True):
            scan_dir_x = not scan_dir_x
            scan_handle_y(board, global_data)
            
    elif not scan_dir_x:
        board.turn_servo_x(-3)

        if is_servo_out_of_bounds(board.get_servo_x(), x=True):
            scan_dir_x = not scan_dir_x
            scan_handle_y(board, global_data)
    
    global_data["scan_dir_x"] = scan_dir_x

def scan_handle_y(board: BoardInterface, global_data: dict):
    scan_dir_y = global_data["scan_dir_y"]

    if scan_dir_y:
        board.turn_servo_y(15)
        if is_servo_out_of_bounds(board.get_servo_y(), x=False):
            scan_dir_y = not scan_dir_y
    elif not scan_dir_y:
        board.turn_servo_y(-15)
        if is_servo_out_of_bounds(board.get_servo_y(), x=False):
            scan_dir_y = not scan_dir_y

    global_data["scan_dir_y"] = scan_dir_y

def is_servo_out_of_bounds(angle: int, x: bool):
    if x:
        return angle >= 180 or angle <= 0
    else:
        return angle >= 180 or angle <= 0

