from gpiozero import Servo
from gpiozero import LED
import cv2
from picamera2 import Picamera2
import time

def convert_angle_to_dutycycle(angle):
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    output = (angle / 90) - 1
    return output

class RaspberryPiZero2:
    _laser: LED
    _servoX: "_Servo"
    _servoY: "_Servo"
    _cameraSize = (640, 640)
    _cameraCenter: tuple[int, int]
    
    class _Servo:
        _servo: Servo
        _currentAngle = 0
        _maxAngle = 180
        _minAngle = 0
        
        def __init__(self, pin, minAngle=0, maxAngle=180):
            self._servo = Servo(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
            self._minAngle = minAngle
            self._maxAngle = maxAngle
        
        def _boundAngle(self, angle):
            if angle < self._minAngle:
                return self._minAngle
            elif angle > self._maxAngle:
                return self._maxAngle
            return angle
        
        def turn(self, angle, debug=False):
            self.setAngle(self._currentAngle + angle, debug)
            
        def setAngle(self, angle, debug=False):
            # Calculate duty cycle to turn to the required angle
            self._currentAngle = self._boundAngle(angle)
            dutyCycle = convert_angle_to_dutycycle(self._currentAngle)
            # Make the servo sleep for a period proportional to the angle it needs to turn
            # Use abs() so sleep time is always positive
            self._servo.value = dutyCycle
            time.sleep(abs(dutyCycle - self._servo.value) * 0.1)
            if debug:
                print(f"Angle: {angle}")
            
        def getAngle(self):
            return self._currentAngle
            
        def cleanup(self):
            self.setAngle(0)
    
    
    def __init__(self, debug=False):
        self._debug = debug

        # Laser Set Up
        self._laser = LED(17)
        
        # Servo Set Up
        self._servoX = self._Servo(13)
        self._servoY = self._Servo(12, minAngle=45, maxAngle=135)
        
        # Set up cam
        self._camera = Picamera2()
        config = self._camera.create_preview_configuration(main={"size": (self._cameraSize[0], self._cameraSize[0] * 2)})
        self._cameraCenter = (self._cameraSize[0] / 2, self._cameraSize[1] / 2)
        self._camera.configure(config)
        self._camera.start()
       

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
            self._laser.on()
        else:
            self._laser.off()
            
    def setDebug(self, debug):
        """
        Sets if debug messages are printed.
        """
        self._debug = debug

    def getCamCenter(self):
        return self._cameraCenter

    def getCamSize(self):
        return self._cameraSize

    def getCamFrame(self):
        frame = self._camera.capture_array()
        # since the camera is actually upside down on the gimbal, we have to flip the frame on the y-axis
        frame = cv2.flip(frame, 0)
        return frame

    def cleanup(self):
        """
        Call this when the program is exiting to clean up the GPIO pins
        """
        self._servoX.cleanup()
        self._servoY.cleanup()
        self.setLaser(0)
        self._camera.close()


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
