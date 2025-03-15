import numpy as np
from ultralytics import YOLO
from abc import ABC, abstractmethod

class YOLOv5(ABC):
    @abstractmethod
    def detect_objects(self, image, conf_thres=0.4):
        pass
    
