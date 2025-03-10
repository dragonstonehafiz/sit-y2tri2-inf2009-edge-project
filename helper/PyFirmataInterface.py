import pyfirmata2
import time

def boundAngle(angle):
    if angle < 0:
        return 0
    elif angle > 180:
        return 180
    return angle

class PyFirmataInterface:
    def __init__(self, port):
        self.board = pyfirmata2.Arduino(port)
        self.servoY = self.board.get_pin('d:6:s')
        self.servoX = self.board.get_pin('d:8:s')
        self.led = self.board.get_pin('d:13:o')
        
        self.servoY.write(90)
        self.servoX.write(90)
        time.sleep(2)
        
    def set_servo_x(self, angle):
        angle = boundAngle(angle)
        self.servoX.write(angle)
        
    def turn_servo_x(self, angle):
        angle = boundAngle(self.servoX.read() + angle)
        self.servoX.write(angle)
        
    def set_servo_y(self, angle):
        angle = boundAngle(angle)
        self.servoY.write(angle)
        
    def turn_servo_y(self, angle):
        angle = boundAngle(self.servoY.read() + angle)
        self.servoY.write(angle)
        
    def set_laser(self, value):
        self.led.write(value)
        
    def close(self):
        self.board.exit()