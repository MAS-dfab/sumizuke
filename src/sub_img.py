import paho.mqtt.client as mqtt
import numpy as np
import cv2
import time
import os

# MQTT Broker Configuration
BROKER = "test.mosquitto.org"  # Public MQTT broker
TOPIC = "craftsx/img"  # Same topic as in Nicla Vision script

# Create a directory for saved images
SAVE_DIR = "captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)


def preprocess_image(img_bytes):
    """Convert received image bytes to a NumPy array and resize."""
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_resized = cv2.resize(img, (320, 320))  # Resize to 320x320
    return img_resized


def on_message(client, userdata, message):
    """Callback function for MQTT message reception."""
    try:
        img_bytes = message.payload
        img = preprocess_image(img_bytes)

        # Display the image
        cv2.imshow("Nicla Vision", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):  # Save image when 's' is pressed
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = os.path.join(SAVE_DIR, f"image_{timestamp}.jpg")
            cv2.imwrite(filename, img)
            print(f"Image saved: {filename}")

        elif key == ord("q"):  # Quit when 'q' is pressed
            client.disconnect()
            cv2.destroyAllWindows()

    except Exception as e:
        print("Error:", e)


# Set up MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER)
client.subscribe(TOPIC)

print("Listening for images from Nicla Vision... Press 's' to save, 'q' to quit.")
client.loop_forever()
