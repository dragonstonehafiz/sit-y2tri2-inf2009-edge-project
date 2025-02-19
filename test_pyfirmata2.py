"""
For this file to work, you need to push the stabdard firmata sketch to the Arduino Uno board before running this code.
"""
import serial.tools.list_ports
import time
from helper.PyFirmataInterface import PyFirmataInterface
from helper.FaceDetector import FaceDetector
from helper.RefreshRateLimiter import RefreshRateLimiter
import cv2

def list_serial_ports():
    """Lists available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")
        

def main():
    list_serial_ports()
    
    serialPort = "/dev/ttyACM0"
    
    # Initialize Interfaces
    arduino = PyFirmataInterface(serialPort)
    arduino.write_LED(1)
    # FPS limiter to reduce number of computations every second
    # Setting rrl value to 10 means in 1 second, the while loop will ideally only run 10 times a second
    rrl = RefreshRateLimiter(10)
    faceDetector = FaceDetector()
    
    # Raspberry Pi Zero can't draw preview, so we have to set to false before running on there
    USE_WEBCAM = False
    DRAW_PREVIEW = True 
    # Open the default camera
    if USE_WEBCAM:
        cap = cv2.VideoCapture(0)
        # Get the default frame width and height
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_width_over_10 = frame_width / 10
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_height_over_10 = frame_height / 10
        centerX = (int)(frame_width / 2)
        centerY = (int)(frame_height / 2)
    else: 
        # Moving this here because PiCameraInterface has libraries that can't be installed on windows (causes crashes at runtime)
        from helper.PiCameraInterface import PiCameraInterface
        picam = PiCameraInterface()
        picam.start()
        frame_width = picam.getSize()[0]
        frame_width_over_10 = frame_width / 12
        frame_height = picam.getSize()[1]
        frame_height_over_10 = frame_height / 12
        centerX = (int)(picam.getCenter()[0])
        centerY = (int)(picam.getCenter()[0])
    
    # Set this timer so that the program can automatically end on pi zero
    start = time.time()
    while True:
        rrl.startFrame()

        if USE_WEBCAM:
            _, frame = cap.read()
        else:
            frame = picam.capture()
        
        now = time.time()
        if (now - start) > 60:
            break
        
        objCenter = faceDetector.detectClosestFace(frame, (centerX, centerY))
        
        # Draw rectangle around the faces
        if objCenter is not None:
            objCenterX = (int)(objCenter[0]) 
            objCenterY = (int)(objCenter[1])
            displacementX = (int)(objCenterX - centerX) / frame_width_over_10
            displacementY = -((int)(objCenterY - centerY) / frame_height_over_10)
            
            if DRAW_PREVIEW:
                cv2.circle(frame, (objCenterX, objCenterY), 5, (255, 255, 255), 50)
                cv2.putText(frame, f'{displacementX:0.2f}, {displacementY:0.2f}', (objCenterX, objCenterY-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 2)
            
            # Only turn the servo if (normalized) distance is larger than 1
            if displacementX >= 1 or displacementX <= -1:
                arduino.turn_servoX((int)(displacementX))
            elif displacementY >= 1 or displacementY <= -1:
                arduino.turn_servoY((int)(-displacementY))

        if DRAW_PREVIEW:
           # Display a point to show the center of the screen
           cv2.circle(frame, (centerX, centerY), 5, (255, 0, 0), 5)
           # Display the captured frame
           cv2.imshow('Camera', frame) 
           
        # Calls sleep to make sure the program runs a limited number of times a single second
        rrl.limit()

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    arduino.write_LED(0)
    arduino.close()

if __name__ == "__main__":
    main()
