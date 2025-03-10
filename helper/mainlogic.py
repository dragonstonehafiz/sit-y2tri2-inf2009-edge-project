from helper.RaspberryPiZero2 import RaspberryPiZero2

def scan_handle_x(pizero: RaspberryPiZero2, scanDir: list[bool, bool]):
    # Turn servo x in either left or right
    # then check if the servo is at max/min
    # if it is, turn the y servo
    if scanDir[0] == True:
        pizero.turn_servo_x(3)

        if is_servo_out_of_bounds(pizero.get_servo_x_angle(), x=True):
            scanDir[0] = not scanDir[0]
            scan_handle_y(pizero, scanDir)
            
    elif scanDir[0] == False:
        pizero.turn_servo_x(-3)

        if is_servo_out_of_bounds(pizero.get_servo_x_angle(), x=True):
            scanDir[0] = not scanDir[0]
            scan_handle_y(pizero, scanDir)

def scan_handle_y(pizero: RaspberryPiZero2, scanDir: list[bool, bool]):
    if scanDir[1] == True:
        pizero.turn_servo_y(15)
        if is_servo_out_of_bounds(pizero.get_servo_y_angle(), x=False):
            scanDir[1] = not scanDir[1]
    elif scanDir[1] == False:
        pizero.turn_servo_y(-15)
        if is_servo_out_of_bounds(pizero.get_servo_y_angle(), x=False):
            scanDir[1] = not scanDir[1]

def is_servo_out_of_bounds(angle: int, x: bool):
    if x:
        return angle >= 180 or angle <= 0
    else:
        return angle >= 135 or angle <= 45

