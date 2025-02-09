import RPi.GPIO as GPIO
import time

class RaspberryPiZero2:
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
            self._currentAngle = self._boundAngle(angle)
            dutyCycle = self._convertAngleToDutyCycle(angle)
            self._servo.ChangeDutyCycle(dutyCycle)
            time.sleep(0.2)
            self._servo.ChangeDutyCycle(0)
            
        def getAngle(self):
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
        
        
    def setServoX(self, angle):
        """
        Set the X servo's current turning angle (only +)
        """
        self._servoX.setAngle(angle)
        
    def turnServoX(self, angle):
        """
        Turns the X servo by a specified angle (+ or -)
        """
        self._servoX.turn(angle)
        
    def setServoY(self, angle):
        """
        Set the Y servo's current turning angle (only +)
        """
        self._servoY.setAngle(angle)
        
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
        
    def turnServoY(self, angle):
        """
        Turns the Y servo by a specified angle (+ or -)
        """
        self._servoY.turn(angle)

    def setLaser(self, val: bool):
        """
        True = ON, False = OFF
        """
        if val > 0:
            GPIO.output(self._laser, GPIO.HIGH)
        else:
            GPIO.output(self._laser, GPIO.LOW)

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
