import cv2
import numpy as np
import onnxruntime
import time

# Load ONNX model
onnx_model = "model/yolov5n_256.onnx"
session = onnxruntime.InferenceSession(onnx_model, providers=["CPUExecutionProvider"])

# Get model input/output details
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Load and preprocess image
img = cv2.imread("image/image.jpg")
img_resized = cv2.resize(img, (256, 256))  # Resize to model input
img_input = img_resized.transpose(2, 0, 1)  # Convert to (C, H, W)
img_input = np.expand_dims(img_input, axis=0).astype(np.float32) / 255.0  # Normalize

startTime = time.time()
# Run inference
outputs = session.run([output_name], {input_name: img_input})[0]

# Extract detections
threshold = 0.4  # Confidence threshold (adjustable)
nms_threshold = 0.5  # IoU threshold for NMS (adjustable)
boxes, scores, class_ids = [], [], []

for detection in outputs[0]:  # Loop over all 25200 anchor points
    x, y, w, h = detection[:4]
    confidence = detection[4]
    class_scores = detection[5:]
    class_id = 14
    class_confidence = class_scores[class_id]

    if confidence > threshold:  # Only keep high-confidence detections
        boxes.append([int(x), int(y), int(w), int(h)])
        scores.append(float(class_confidence))
        class_ids.append(class_id)

# Apply Non-Maximum Suppression (NMS)
indices = cv2.dnn.NMSBoxes(boxes, scores, threshold, 0.5)

print(len(boxes))

if len(indices) > 0:
    indices = indices.flatten()  # Convert indices to 1D array
    for i in indices:
        x, y, w, h = boxes[i]
        x -= (int)(w / 2)
        y -= (int)(h / 2)
        class_name = f"Class {class_ids[i]}"
        print(f"{x}, {y}")

endTime = time.time()

print(f"Inference Time {(endTime - startTime):0.2f}s")
