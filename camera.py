import cv2
from picamera2 import Picamera2
import time

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (480, 480)})
    picam2. configure(config)
    picam2.start()

    time.sleep(2)
    
    while True:
        frame = picam2.capture_array()
        cv2.imshow("Raspberry Pi Camera", frame)
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
    
    cv2.destroyAllWindows()
    picam2.close()