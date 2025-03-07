import RPi.GPIO as GPIO
import cv2
import time

class RaspberryPiZero2:
    _laser: int
    _servoX: "_Servo"
    _servoY: "_Servo"
    
    class _Servo:
        _currentAngle = 0
        _maxAngle = 180
        _minAngle = 0
        
        def __init__(self, pin, minAngle=0, maxAngle=180):
            self._pin = pin
            GPIO.setup(self._pin, GPIO.OUT)
            self._servo = GPIO.PWM(self._pin, 50)
            self._maxAngle = maxAngle
            self._minAngle = minAngle
            self._servo.start(0)
            self.setAngle(minAngle)
        
        def _convertAngleToDutyCycle(self, angle):
            if angle < 0:
                angle = 0
            elif angle > 180:
                angle = 180
            return 2 + (angle / 18.0)
        
        def _boundAngle(self, angle):
            if angle < self._minAngle:
                return self._minAngle
            elif angle > self._maxAngle:
                return self._maxAngle
            return angle
        
        def turn(self, angle, debug=False):
            self.setAngle(self._currentAngle + angle, debug)
            
        def setAngle(self, angle, debug=False):
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
            if debug:
                print(f"Angle: {angle}")
            
        def getAngle(self):
            return self._currentAngle
            
        def cleanup(self):
            self.setAngle(0)
            self._servo.stop()
    
    
    def __init__(self, debug=False):
        self._debug = debug
        GPIO.setmode(GPIO.BCM)

        # Laser Set Up
        self._laser = 17
        GPIO.setup(self._laser, GPIO.OUT)
        
        # Servo Set Up
        self._servoX = self._Servo(13)
        self._servoY = self._Servo(12, minAngle=45, maxAngle=135)
       

    def setServoX(self, angle):
        """
        Set the X servo's current turning angle (only +)
        """
        self._servoX.setAngle(angle, debug=self._debug)
        
    def turnServoX(self, angle):
        """
        Turns the X servo by a specified angle (+ or -)
        """
        self._servoX.turn(angle, debug=self._debug)
        
    def setServoY(self, angle):
        """
        Set the Y servo's current turning angle (only +)
        """
        self._servoY.setAngle(angle, debug=self._debug)
        
    def turnServoY(self, angle):
        """
        Turns the Y servo by a specified angle (+ or -)
        """
        self._servoY.turn(angle, debug=self._debug)

    def getServoXAngle(self):
        """
        Get the current angle of the X servo
        """
        return self._servoX.getAngle()
    
    def getServoYAngle(self):
        """
        Get the current angle of the Y servo
        """
        return self._servoY.getAngle()
        
    def setLaser(self, val: bool):
        """
        True = ON, False = OFF
        """
        if val > 0:
            GPIO.output(self._laser, GPIO.HIGH)
        else:
            GPIO.output(self._laser, GPIO.LOW)
            
    def setDebug(self, debug):
        """
        Sets if debug messages are printed.
        """
        self._debug = debug

    def cleanup(self):
        """
        Call this when the program is exiting to clean up the GPIO pins
        """
        self._servoX.cleanup()
        self._servoY.cleanup()
        self.setLaser(0)
        GPIO.cleanup()


# Main program
if __name__ == "__main__":
    try:
        piZero = RaspberryPiZero2()
        while True:
            piZero.setServoX(0)
            time.sleep(1)

            piZero.setServoX(180)
            time.sleep(1)

            piZero.setServoY(180)
            time.sleep(1)

            piZero.setServoY(0)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
        piZero.cleanup()
