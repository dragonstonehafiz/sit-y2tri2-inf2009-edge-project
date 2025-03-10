from helper.BoardInterface import BoardInterface

import RPi.GPIO as GPIO
import cv2
import time

class RaspberryPiZero2(BoardInterface):
    _laser: int
    _servoX: "_Servo"
    _servoY: "_Servo"
    
    class _Servo:
        _currentAngle = 0
        
        def __init__(self, pin):
            self._pin = pin
            GPIO.setup(self._pin, GPIO.OUT)
            self._servo = GPIO.PWM(self._pin, 50)
            self._servo.start(0)
        
        def _convertAngleToDutyCycle(self, angle):
            if angle < 0:
                angle = 0
            elif angle > 180:
                angle = 180
            return 2 + (angle / 18.0)
        
        def _boundAngle(self, angle):
            if angle < 0:
                return 0
            elif angle > 180:
                return 180
            return angle
        
        def turn(self, angle):
            self.setAngle(self._currentAngle + angle)
            
        def setAngle(self, angle):
            # Save previous angle to calculate how long the system should wait before stopping the servo
            prevAngle = self._currentAngle
            # Calculate duty cycle to turn to the required angle
            self._currentAngle = self._boundAngle(angle)
            dutyCycle = self._convertAngleToDutyCycle(angle)
            self._servo.ChangeDutyCycle(dutyCycle)
            # Make the servo sleep for a period proportional to the angle it needs to turn
            # Use abs() so sleep time is always positive
            # Turning from 0 to 180 degrees should take 0.25 seconds
            # Turning from 0 to 45 degrees should take 0.05 seconds
            sleepTime = abs(self._currentAngle - prevAngle) / 180.0 * 0.25
            sleepTime = max(sleepTime, 0.05)
            time.sleep(sleepTime)
            self._servo.ChangeDutyCycle(0)
            
        def get_angle(self):
            return self._currentAngle
            
        def cleanup(self):
            self.setAngle(0)
            self._servo.stop()
    
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # Laser Set Up
        self._laser = 17
        GPIO.setup(self._laser, GPIO.OUT)
        
        # Servo Set Up
        self._servoX = self._Servo(13)
        self._servoY = self._Servo(12)
       

    def set_servo_x(self, angle):
        self._servoX.setAngle(angle)
        
    def turn_servo_x(self, angle):
        self._servoX.turn(angle)
        
    def set_servo_y(self, angle):
        self._servoY.setAngle(angle)
        
    def turn_servo_y(self, angle):
        self._servoY.turn(angle)

    def get_servo_x(self):
        return self._servoX.get_angle()
    
    def get_servo_y(self):
        return self._servoY.get_angle()
        
    def set_laser(self, val: bool):
        if val > 0:
            GPIO.output(self._laser, GPIO.HIGH)
        else:
            GPIO.output(self._laser, GPIO.LOW)

    def close(self):
        self._servoX.cleanup()
        self._servoY.cleanup()
        self.set_laser(0)
        GPIO.cleanup()


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
