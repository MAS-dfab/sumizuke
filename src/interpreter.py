import paho.mqtt.client as mqtt
import numpy as np
import cv2

# MQTT Broker Configuration
BROKER = "test.mosquitto.org"  # Public MQTT broker
TOPIC = "openmv/test"  # Same topic as in Nicla Vision script

from ultralytics import YOLO 

path = "../models/cross_yolov8n.pt"
model = YOLO(path)


def preprocess_image(img_bytes):
    """Convert received image bytes to a NumPy array and resize for FOMO."""
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_resized = cv2.resize(img, (320  , 320))  # Resize to 256x256
    return img_resized


def infer_yolo(img):
    """Perform inference on the image using the YOLO model."""
    results = model(img)
    boxess = []
    classes = []
    for result in results:
        boxes = result.boxes
        boxess.append(boxes.xywh)
        # Get result class for each box
        class_indices = result.boxes.cls.cpu().numpy().astype(int)  # Class indices
        print(class_indices)
        classes.append(class_indices)

    return boxess, classes


def on_message(client, userdata, message):
    """Callback function for MQTT message reception."""
    try:
        img_bytes = message.payload
        img_array = preprocess_image(img_bytes)
        boxes, classes = infer_yolo(img_array)

        # Draw boxes on the image
        for box, clas in zip(boxes, classes):
            # Box is a tensor of [x, y, w, h]
    
            for b, c in zip(box, clas):
                x, y, w, h = b
                x1, y1, x2, y2 = (
                    int(x - w / 2),
                    int(y - h / 2),
                    int(x + w / 2),
                    int(y + h / 2),
                )
                if c == 0:
                    # make red
                    cv2.rectangle(img_array, (x1, y1), (x2, y2), (0, 0, 255), 2)
                else:
                    cv2.rectangle(img_array, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # cv2.rectangle(img_array, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
        # Display the image
        cv2.imshow("Nicla Vision", img_array)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            client.disconnect()
            cv2.destroyAllWindows()

    except Exception as e:
        print("Error:", e)


# Set up MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER)
client.subscribe(TOPIC)

print("Listening for images from Nicla Vision...")
client.loop_forever()
