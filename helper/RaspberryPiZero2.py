import RPi.GPIO as GPIO
import time

class RaspberryPiZero2:
    def __init__(self):
        self._servoXPin = 17  # Servo 1 GPIO Pin
        self._servoYPin = 18  # Servo 2 GPIO Pin

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._servoXPin, GPIO.OUT)
        GPIO.setup(self._servoYPin, GPIO.OUT)

        # Start PWM at 50Hz
        self._servoX = GPIO.PWM(self._servoXPin, 50)
        self._servoX.start(0)
        self._servoY = GPIO.PWM(self._servoYPin, 50)
        self._servoY.start(0)
        
        
    def _convertAngleToDutyCycle(self, angle):
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        return 2 + (angle / 18.0)
        
        
    def setServoX(self, angle):
        dutyCycle = self._convertAngleToDutyCycle(angle)
        self._servoX.ChangeDutyCycle(dutyCycle)
        time.sleep(0.5)
        self._servoX.ChangeDutyCycle(0)
        
        
    def setServoY(self, angle):
        dutyCycle = self._convertAngleToDutyCycle(angle)
        self._servoX.ChangeDutyCycle(dutyCycle)
        time.sleep(0.5)
        self._servoX.ChangeDutyCycle(0)


    def cleanup(self):
        self.setServoX(0)
        self.setServoY(0)
        self._servoX.stop()
        self._servoY.stop()
        GPIO.cleanup()


# Main program
if __name__ == "__main__":
    try:
        piZero = RaspberryPiZero2()
        while True:
            piZero.setServoX(0)
            piZero.setServoY(0)
            time.sleep(1)

            piZero.setServoX(90)
            piZero.setServoY(90)
            time.sleep(1)

            piZero.setServoX(180)
            piZero.setServoY(180)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
        piZero.cleanup()
