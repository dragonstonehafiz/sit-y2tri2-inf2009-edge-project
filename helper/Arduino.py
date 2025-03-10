from helper.BoardInterface import BoardInterface
import pyfirmata2
import time

def boundAngle(angle):
    if angle < 0:
        return 0
    elif angle > 180:
        return 180
    return angle

class Arduino(BoardInterface):
    def __init__(self, port):
        self._board = pyfirmata2.Arduino(port)
        self._servo_y: pyfirmata2.Pin = self._board.get_pin('d:6:s')
        self._servo_x: pyfirmata2.Pin = self._board.get_pin('d:8:s')
        self._led: pyfirmata2.Pin = self._board.get_pin('d:13:o')
        
        self.set_servo_x(90)
        self.set_servo_y(90)
        time.sleep(1)

    def get_servo_x(self):
        return self._servo_x.read()
    
    def get_servo_y(self):
        return self._servo_y.read()
        
    def set_servo_x(self, angle):
        angle = boundAngle(angle)
        self._servo_x.write(angle)
        
    def turn_servo_x(self, angle):
        angle = boundAngle(self.get_servo_x() + angle)
        self._servo_x.write(angle)
        
    def set_servo_y(self, angle):
        angle = boundAngle(angle)
        self._servo_y.write(angle)
        
    def turn_servo_y(self, angle):
        angle = boundAngle(self.get_servo_y() + angle)
        self._servo_y.write(angle)
        
    def set_laser(self, value):
        self._led.write(value)
        
    def close(self):
        self._board.exit()