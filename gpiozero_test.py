from gpiozero import Servo
from gpiozero import LED
import time

if __name__ == "__main__":
    servoX = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servoY = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    led = LED(17)
    time.sleep(1)
    
    servoX.value = 0.0
    for i in range(3):
        led.on()
        for dutycycle in range(0, 100, 5):
            print(dutycycle)
            servoX.value = dutycycle / 100
            time.sleep(0.1)
        
        led.off()
        for dutycycle in range(100, 0, -5):
            print(dutycycle)
            servoX.value = dutycycle / 100
            time.sleep(0.1)
            
        led.on()
        for dutycycle in range(0, -100, -5):
            print(dutycycle)
            servoX.value = dutycycle / 100
            time.sleep(0.1)
            
        led.off()
        for dutycycle in range(-100, 0, 5):
            print(dutycycle)
            servoX.value = dutycycle / 100
            time.sleep(0.1)
            