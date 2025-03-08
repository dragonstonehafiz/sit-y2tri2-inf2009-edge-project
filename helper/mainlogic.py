from RaspberryPiZero2 import RaspberryPiZero2

def scan_handle_x(pizero: RaspberryPiZero2, scanDir: list[bool, bool]):
    # Turn servo x in either left or right
    # then check if the servo is at max/min
    # if it is, turn the y servo
    if scanDir[0] == True:
        pizero.turnServoX(5)

        if is_servo_out_of_bounds(pizero.getServoXAngle(), x=True):
            scanDir[0] = not scanDir[0]
            scan_handle_y(pizero, scanDir)
            
    elif scanDir[0] == False:
        pizero.turnServoX(-5)

        if is_servo_out_of_bounds(pizero.getServoXAngle(), x=True):
            scanDir[0] = not scanDir[0]
            scan_handle_y(pizero, scanDir)

def scan_handle_y(pizero: RaspberryPiZero2, scanDir: list[bool, bool]):
    if scanDir[1] == True:
        pizero.turnServoY(5)
        if is_servo_out_of_bounds(pizero.getServoYAngle(), x=False):
            scanDir[1] = not scanDir[1]
    elif scanDir[1] == False:
        pizero.turnServoY(-1)
        if is_servo_out_of_bounds(pizero.getServoYAngle(), x=False):
            scanDir[1] = not scanDir[1]

def is_servo_out_of_bounds(angle: int, x: bool):
    if x:
        return angle >= 180 or angle <= 0
    else:
        return angle >= 135 or angle <= 45

