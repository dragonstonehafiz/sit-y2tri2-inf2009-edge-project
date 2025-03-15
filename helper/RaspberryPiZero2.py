from helper.BoardInterface import BoardInterface

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo, LED
import cv2
import time

class RaspberryPiZero2(BoardInterface):
    _laser: LED
    _servoX: AngularServo
    _servoY: AngularServo
    _factory: PiGPIOFactory
    
    def __init__(self):
        self._factory = PiGPIOFactory()
        self._servoX = AngularServo(pin=13, pin_factory=self._factory)
        self._servoY = AngularServo(pin=12, pin_factory=self._factory)

        # Laser Set Up
        self._laser = LED(pin=17, pin_factory=self._factory)

        # Default Variables
        self._servoX.angle = 0
        self._servoY.angle = 0
        self._laser.off()

    def _boundAngle(self, angle: float) -> float:
        """Converts angle from 0 to 180 to -90 to 90"""
        if angle > 180:
            return 90
        elif angle < 0:
            return -90
        else:
            return angle - 90
       
    def set_servo_x(self, angle):
        self._servoX.angle = self._boundAngle(angle)
        
    def turn_servo_x(self, angle):
        self.set_servo_x(self.get_servo_x() + angle)
        
    def set_servo_y(self, angle):
        self._servoY.angle = self._boundAngle(angle)
        
    def turn_servo_y(self, angle):
        self.set_servo_x(self.get_servo_y() + angle)

    def get_servo_x(self):
        return self._servoX.angle
    
    def get_servo_y(self):
        return self._servoY.angle
        
    def set_laser(self, val: bool):
        if val:
            self._laser.on()
        else:
            self._laser.off()

    def close(self):
        self._laser.close()
        self._servoX.close()
        self._servoY.close()

# Main program
if __name__ == "__main__":
    try:
        piZero = RaspberryPiZero2()
        while True:
            piZero.set_servo_x(0)
            time.sleep(1)

            piZero.set_servo_x(180)
            time.sleep(1)

            piZero.set_servo_y(180)
            time.sleep(1)

            piZero.set_servo_y(0)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
        piZero.close()
