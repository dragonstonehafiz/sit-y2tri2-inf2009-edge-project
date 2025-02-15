import cv2
from picamera2 import Picamera2
import time
from helper.FaceDetector import FaceDetector

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (480, 480)})
    picam2. configure(config)
    picam2.start()
    faceDetector = FaceDetector()

    time.sleep(2)
    
    while True:
        frame = picam2.capture_array()
        face = faceDetector.detect(frame)

        # Draw rectangle around the faces
        for (x, y, w, h) in face:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.putText(frame, f'x:{x:0.2f}, y:{y:0.2f}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        
        # Display the captured frame
        cv2.imshow("Raspberry Pi Camera", frame)
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
    
    cv2.destroyAllWindows()
    picam2.close()