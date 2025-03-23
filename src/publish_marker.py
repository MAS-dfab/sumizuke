import paho.mqtt.client as mqtt
import numpy as np
import time
import cv2 as cv
import os, sys
import threading

# Import the CCTDecodeRelease module
module_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..","../../crafts_extended"))
module_path = os.path.join(module_path, 'CCTDecode', 'CCTDecode')
if module_path not in sys.path:
    sys.path.append(module_path)

import CCTDecodeRelease as cct

MQTT_SERVER = "test.mosquitto.org"
IMAGE_TOPIC = "craftsx/img"
MODE_TOPIC = "craftsx/mode"
ID_TOPIC = "craftsx/id"

# Global variable to store the mode
mode = 1  # Default mode
mode_lock = threading.Lock()


from ultralytics import YOLO 

path = "../models/cross_yolov8n.pt"
model = YOLO(path)


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


def update_mode():
    """ Continuously listens for mode updates in a separate thread. """
    def on_mode_message(client, userdata, msg):
        global mode
        try:
            new_mode = int(msg.payload.decode())
            with mode_lock:
                mode = new_mode
            print(f"Mode updated to: {mode}")
        except ValueError:
            print("Invalid mode received")
    
    mode_client = mqtt.Client()
    mode_client.on_connect = lambda c, u, f, r: c.subscribe(MODE_TOPIC)
    mode_client.on_message = on_mode_message
    mode_client.connect(MQTT_SERVER, 1883, 60)
    mode_client.loop_forever()

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(IMAGE_TOPIC)

# Callback when image message is received
def on_image_message(client, userdata, msg):
    print("Image Received")
    nparr = np.frombuffer(msg.payload, np.uint8)
    img_np = cv.imdecode(nparr, cv.IMREAD_COLOR)
    
    with mode_lock:
        current_mode = mode
    
    if current_mode == 2:
        code_table, img = cct.CCT_extract(img_np, 12, 0.85, 'black')
        print("Code Table: ", code_table)
        if code_table:
            client.publish(ID_TOPIC, str(code_table[0][0]))
    else:
        print("Processing image in mode", current_mode)
        # Add alternative image processing logic here
        boxes, classes = infer_yolo(img_np)

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
                    cv.rectangle(img_np, (x1, y1), (x2, y2), (0, 0, 255), 2)
                else:
                    cv.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
    cv.imshow("Nicla Vision", img_np)
    cv.waitKey(1)

client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add(IMAGE_TOPIC, on_image_message)
client.connect(MQTT_SERVER, 1883, 60)

# Start mode listener in a separate thread
mode_thread = threading.Thread(target=update_mode, daemon=True)
mode_thread.start()

client.loop_forever()
