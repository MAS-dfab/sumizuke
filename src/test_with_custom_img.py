from ultralytics import YOLO

# Relative path to YOLOv5 model
path = "../models/cross_yolov8n.pt"
model = YOLO(path)

# Test on custom image
img = "C:/Users/akango/Downloads/data/resized_20250314_154112.jpg"
results = model(img)

# Process results list
for result in results:
    # Get result class
    print(f"Class: {result.names}")
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()  # display to screen