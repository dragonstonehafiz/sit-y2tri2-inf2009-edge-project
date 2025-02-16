from gpiozero import Servo
from gpiozero import LED
import time

def convert_angle_to_dutycycle(angle):
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    output = (angle / 90) - 1
    print(angle, output)
    return output

if __name__ == "__main__":
    servoX = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servoY = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    led = LED(17)
    time.sleep(1)
    
    servoX.value = -1.0
    time.sleep(1)
    for angle in range (0, 181, 3):
        # print(angle)
        servoX.value = convert_angle_to_dutycycle(angle)
        time.sleep(0.1)
    
    time.sleep(1)

    for angle in range (180, -2, -3):
        # print(angle)
        servoX.value = convert_angle_to_dutycycle(angle)
        time.sleep(0.1)
    
    time.sleep(1)

    for angle in range (180, -2, -3):
        # print(angle)
        servoY.value = convert_angle_to_dutycycle(angle)
        time.sleep(0.1)

    time.sleep(1.0)
    
    servoY.value = 0.0
    servoX.value = 0.0
    time.sleep(1)
