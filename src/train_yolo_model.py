import os
from ultralytics import YOLO

# data path and output path
data = os.path.join(os.path.dirname(__file__), "data.yaml")
output = os.path.join(os.path.dirname(__file__), "..", "models", "cross_yolov8n.pt")

# Load a pre-trained YOLOv8 model
model = YOLO("yolov8n.pt") 

# Train on data.yaml
model.train(data=data, epochs=100, imgsz=240)

# Save the model to a file
model.save(output)