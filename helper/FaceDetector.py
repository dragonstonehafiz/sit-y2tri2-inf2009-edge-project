import cv2

class FaceDetector:
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        return faces

    def detectWithConfidence(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces, confidence = self.face_classifier.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        return faces, confidence
    
    def detectClosestFace(self, frame, center: tuple[int, int]):
        """Returns the center of the face closest to the center of the screen.
        """
        faces = self.detect(frame)
        if len(faces) == 0:
            return None
        
        shortestDistance = float("inf")
        for (x, y, w, h) in faces:
            # Calculate the position of the current face
            objectCenterX = x + w / 2
            objectCenterY = y + h / 2
            # Calculate the distance of that face to the center of the screen
            displacement = (objectCenterX - center[0], objectCenterY - center[1])
            distance = displacement[0] ** 2 + displacement[1] ** 2
            # Update tracker if the current face is the closest
            if distance < shortestDistance:
                shortestDistance = distance
                closestFace = (objectCenterX, objectCenterY)
                
        return closestFace
    
    