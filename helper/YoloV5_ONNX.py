import cv2
import numpy as np
import onnxruntime as ort
import time
try:
    from helper.YoloV5_Base import YOLOv5
except ModuleNotFoundError:
    from YoloV5_Base import YOLOv5

class YoloV5_ONNX(YOLOv5):
    def __init__(self, model_path, image_size):
        print(f"Loading {model_path}")
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL  # Enable all optimizations

        self.session = ort.InferenceSession(model_path, sess_options=so, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.class_id = 14  # Bird class index (update if needed)
        self.image_size = image_size

    def preprocess(self, image):
        """Prepares the image for YOLOv5 model."""
        img_input = cv2.resize(image, self.image_size)
        img_input = img_input.transpose(2, 0, 1)  # Convert to (C, H, W)
        img_input = np.expand_dims(img_input, axis=0).astype(np.float32) / 255.0  # Normalize
        return img_input

    def detect_objects(self, image, conf_thres=0.4):
        """Runs inference and extracts (x, y, w, h, confidence, class_id)."""
        img_input = self.preprocess(image)
        outputs = self.session.run([self.output_name], {self.input_name: img_input})[0]

        boxes, scores = [], []

        # Extract relevant detections
        for detection in outputs[0]:  # Loop over all detections
            x, y, w, h = detection[:4]
            confidence = detection[4]
            class_scores = detection[5:]
            class_confidence = class_scores[self.class_id]

            if confidence > 0.4:  # Apply confidence threshold
                boxes.append([int(x), int(y), int(w), int(h)])
                scores.append(float(class_confidence))

        # Apply Non-Maximum Suppression (NMS)
        indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=conf_thres, nms_threshold=0.5)

        # print(len(boxes))  # Print number of detected objects before NMS

        detections = []
        if len(indices) > 0:
            indices = indices.flatten()
            for i in indices:
                x, y, w, h = boxes[i]
                # x -= int(w / 2)
                # y -= int(h / 2)
                detections.append((x, y))
                # print(f"{x}, {y}")  # Print (x, y) as requested


        return detections

    def render_detections(self, image, objDetected):
        """Draws detected bounding boxes on the image."""
        for (x, y) in objDetected:
            cv2.circle(image, (x, y), 5, (0, 255, 0), 5)

        return image

# ✅ **Run Detection**
if __name__ == "__main__":
    image_path = "image/myna.jpg"
    # image_path = "image/other.jpg"
    image = cv2.imread(image_path)

    RENDER = True
    img_size = 160
    model = YoloV5_ONNX(f"model/yolov5n_{img_size}.onnx", (img_size, img_size))

    times = []
    for i in range(0, 60):
        startTime = time.time()
        objDetected = model.detect_objects(image)
        endTime = time.time()

        elapsedTime = endTime - startTime
        if elapsedTime < 1:
            print(f"Inference Time {elapsedTime * 1000:0.2f}ms")
        else:
            print(f"Inference Time {elapsedTime:0.2f}s")

        times.append(elapsedTime)

        if RENDER:
            # Render and show detections
            image = cv2.resize(image, model.image_size)
            image = model.render_detections(image, objDetected)
            image = cv2.resize(image, (500, 500))
        
            cv2.imshow("Bird Detection", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    print(f"Average Inference Time: {sum(times)/len(times):.2f}s")
    if RENDER:
        cv2.destroyAllWindows()
