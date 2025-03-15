from ultralytics import YOLO
from helper.YoloV5_Base import YOLOv5

class YOLOv5_Ultralytics(YOLOv5):
    def __init__(self, model_name="yolov5n"):
        """
        Initializes the YOLOv5 model.
        :param model_name: Model name (e.g., 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x').
        """
        self.model = YOLO(f"model/{model_name}.pt")  # Auto-downloads model if not found

    def detect_objects(self, image, conf_thres=0.4) -> list:
        """
        Runs YOLOv5 detection on a given image.
        :param image: Input image (NumPy array, BGR format).
        :param target_class: COCO class ID to filter (default: 14 for birds).
        :param conf_thres: Confidence threshold.
        :return: List of detected objects [(centerX, centerY)].
        """
        results = self.model.predict(image, conf=conf_thres, verbose=False)

        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                
                if cls == 14:  # Filter only birds
                    centerX = (x1 + x2) / 2
                    centerY = (y2 + y1) / 2

                    detections.append(((int)(centerX), (int)(centerY)))
        
        return detections
    
