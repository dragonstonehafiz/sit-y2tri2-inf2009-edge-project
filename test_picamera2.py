import cv2
from picamera2 import Picamera2
import time
from helper.FaceDetector import FaceDetector

def normalizeDisplacement(displacement: tuple[int, int], frameSize: tuple[int, int]) -> tuple[int, int]:
    """
    Normalizes the displacement of an object from the center of the screen.
    """
    xDisplacement, yDisplacement = displacement
    xDisplacement = (int) (xDisplacement / (frameSize[0] / 10))
    yDisplacement = (int) (yDisplacement / (frameSize[1] / 10))
    return (xDisplacement, yDisplacement)

def getObjectDisplacement(objectCenter, screenCenter, screenSize) -> tuple[int, int]:
    """
    Returns the displacement of an object from the center of the screen.
    """
    xDisplacement = objectCenter[0] - screenCenter[0]
    yDisplacement = objectCenter[1] - screenCenter[1]
    return normalizeDisplacement((xDisplacement, yDisplacement), screenSize)

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (480, 480)})
    picam2. configure(config)
    picam2.start()
    faceDetector = FaceDetector()

    time.sleep(2)

    screenCenter = (240, 240)
    screenSize = (480,480)
    
    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 0)
        face = faceDetector.detect(frame)

        # Draw rectangle around the faces
        for (x, y, w, h) in face:
            objectCenter = ((int) (x + w / 2), (int) (y + h / 2))
            displacementX, displacementY = getObjectDisplacement(objectCenter, screenCenter, screenSize)
            cv2.circle(frame, (objectCenter[0], objectCenter[1]), 5, (0, 255, 0), 5)
            cv2.putText(frame, f'{displacementX:0.2f},{displacementY:0.2f}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        
        # Display the captured frame
        cv2.imshow("Raspberry Pi Camera", frame)
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
    
    cv2.destroyAllWindows()
    picam2.close()