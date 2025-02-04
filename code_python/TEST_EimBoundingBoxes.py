import cv2
from edge_impulse_linux.image import ImageImpulseRunner
import time

# Open the default camera
videoCaptureID = 0
cap = cv2.VideoCapture(videoCaptureID)

# Load eim model
modelfile = "model/detect-controller-v9.eim"
# modelfile = "model/bird-detect-model-v1.eim"
objDetRunner = ImageImpulseRunner(modelfile)
try:
    model_info = objDetRunner.init()
    labels = model_info['model_parameters']['labels']
    print(f"Model {modelfile} successfully loaded!")
except Exception as e:
    print(f"Error Occured Aborting")
    print(f"Error: {e}")
    quit()

lastFrameTime = time.time()
thisFrameTime = time.time()

while True:
    thisFrameTime = time.time()
    # Read the frame
    ret, frame = cap.read()
    
    # Get the features and cropped image from the frame
    # The features will be used to do inference
    # The cropped image will be use for rendering the camera to the screen
    # We can also crop the image by 'left' or 'right'
    features, cropped = objDetRunner.get_features_from_image(frame, crop_direction_x='center', crop_direction_y='center')
    
    # Now perform inference and find all bounding boxes
    response = objDetRunner.classify(features)
    if "bounding_boxes" in response['result'].keys():
        highest_confidence = 0
        highest_confidence_bb = None
        for bb in response['result']['bounding_boxes']:
            # Skip objects that are not controllers
            if bb["label"] not in ["controller", "bird"]:
                continue
            # I think value is the confidence score
            value = bb["value"]
            if value < 0.9:
                continue
            elif value > highest_confidence:
                highest_confidence = value
                highest_confidence_bb = bb
                
        # Draw the bounding box for the highes confidence object
        if highest_confidence_bb is not None:
            bb = highest_confidence_bb
            x, y = highest_confidence_bb['x'], highest_confidence_bb['y']
            w, h = highest_confidence_bb['width'], highest_confidence_bb['height']
            label = highest_confidence_bb['label']
            cv2.rectangle(cropped, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(cropped, f"{label}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
    
    
    # Track total number of frames elapsed
    elapsed_time = thisFrameTime - lastFrameTime
    cv2.putText(cropped, f"{1/elapsed_time:0.2f}fps", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    lastFrameTime = thisFrameTime
    # Display the captured frame
    cv2.imshow('Camera View', cropped)
    
    
    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
    
cap.release()
