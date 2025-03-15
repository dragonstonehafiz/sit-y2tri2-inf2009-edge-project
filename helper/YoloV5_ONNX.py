import cv2
import numpy as np
import onnxruntime
import time

class YoloV5_ONNX:
    def __init__(self, model_path="model/yolov5n_256.onnx"):
        self.session = onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.class_id = 14  # Bird class index (update if needed)

    def preprocess(self, image):
        """Prepares the image for YOLOv5 model."""
        img_input = image.transpose(2, 0, 1)  # Convert to (C, H, W)
        img_input = np.expand_dims(img_input, axis=0).astype(np.float32) / 255.0  # Normalize
        return img_input

    def detect_objects(self, image):
        """Runs inference and extracts (x, y, w, h, confidence, class_id)."""
        img_input = self.preprocess(image)

        startTime = time.time()
        outputs = self.session.run([self.output_name], {self.input_name: img_input})[0]

        boxes, scores, class_ids = [], [], []

        # Extract relevant detections
        for detection in outputs[0]:  # Loop over all detections
            x, y, w, h = detection[:4]
            confidence = detection[4]
            class_scores = detection[5:]
            class_confidence = class_scores[self.class_id]

            if confidence > 0.4:  # Apply confidence threshold
                boxes.append([int(x), int(y), int(w), int(h)])
                scores.append(float(class_confidence))
                class_ids.append(self.class_id)

        # Apply Non-Maximum Suppression (NMS)
        indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.4, nms_threshold=0.5)

        print(len(boxes))  # Print number of detected objects before NMS

        detections = []
        if len(indices) > 0:
            indices = indices.flatten()
            for i in indices:
                x, y, w, h = boxes[i]
                # x -= int(w / 2)
                # y -= int(h / 2)
                detections.append((x, y))
                print(f"{x}, {y}")  # Print (x, y) as requested

        endTime = time.time()
        print(f"Inference Time {(endTime - startTime):0.2f}s")

        return detections

    def render_detections(self, image, objDetected):
        """Draws detected bounding boxes on the image."""
        for (x, y) in objDetected:
            cv2.circle(image, (x, y), 5, (0, 255, 0), 5)

        return image

# ✅ **Run Detection**
if __name__ == "__main__":
    image_path = "image/image.jpg"
    image = cv2.imread(image_path)
    img_resized = cv2.resize(image, (256, 256))

    model = YoloV5_ONNX("model/yolov5n_256.onnx")
    objDetected = model.detect_objects(img_resized)

    # Render and show detections
    # image = model.render_detections(img_resized, objDetected)
    # cv2.imshow("Bird Detection", img_resized)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
