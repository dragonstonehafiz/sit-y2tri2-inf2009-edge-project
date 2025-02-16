from gpiozero import Servo
from gpiozero import LED
import time

if __name__ == "__main__":
    servoX = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servoY = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    led = LED(17)
    
    while True:
        led.on()
        servoX.value = 0.5
        time.sleep(1)
        
        led.off()
        servoX.value = 1.0
        time.sleep(1)
        
        led.on()
        servoX.value = 0.5
        time.sleep(1)
        
        led.off()
        servoX.value = 0.0
        time.sleep(1)