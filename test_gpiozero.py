from gpiozero import Servo
from gpiozero import LED
import time

def convert_angle_to_dutycycle(angle):
    return (angle + 1) / 90 - 1

if __name__ == "__main__":
    servoX = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servoY = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    led = LED(17)
    time.sleep(1)
    
    servoX.value = -1.0
    time.sleep(4)
    for angle in range (-90, 90, 5):
        print(angle)
        servoX.value = convert_angle_to_dutycycle(angle)
        time.sleep(0.1)
    
    for angle in range (90, -90, -5):
        print(angle)
        servoX.value = convert_angle_to_dutycycle(angle)
        time.sleep(0.1)
            
    servoX.value = 0.0
    time.sleep(1)