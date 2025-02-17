import cv2
from helper.FaceDetector import FaceDetector
from helper.RefreshRateLimiter import RefreshRateLimiter
import pyfirmata2

if __name__ == '__main__':
    # Open the default camera
    cap = cv2.VideoCapture(0)
    faceDetector = FaceDetector()
    rrl = RefreshRateLimiter(12)

    # Get the default frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_width_over_10 = frame_width / 10
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_height_over_10 = frame_height / 10

    while True:
        rrl.startFrame()
        # Read the frame
        ret, frame = cap.read()
        
        faces = faceDetector.detect(frame)
        centerX = (int)(frame_width / 2)
        centerY = (int)(frame_height / 2)
        
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            objCenterX = (int)(x + w / 2) 
            objCenterY = (int)(y + h / 2)
            displacementX = (int)(objCenterX - centerX) / frame_width_over_10
            displacementY = -((int)(objCenterY - centerY) / frame_height_over_10)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.circle(frame, (objCenterX, objCenterY), 5, (0, 255, 0), 5)
            cv2.putText(frame, f'{displacementX:0.2f}, {displacementY:0.2f}', (objCenterX, objCenterY-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 2)

        cv2.circle(frame, (centerX, centerY), 5, (255, 0, 0), 5)
        # Display the captured frame
        cv2.imshow('Camera', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break
        
        rrl.limit()

    cap.release()