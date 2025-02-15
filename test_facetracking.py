import cv2
from helper.FaceDetector import FaceDetector

if __name__ == '__main__':
    # Open the default camera
    cap = cv2.VideoCapture(0)
    faceDetector = FaceDetector()

    # Get the default frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        # Read the frame
        ret, frame = cap.read()
        
        faces = faceDetector.detect(frame)
        
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.putText(frame, f'x:{x:0.2f}, y:{y:0.2f}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

        # Display the captured frame
        cv2.imshow('Camera', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()