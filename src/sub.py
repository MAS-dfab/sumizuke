#r: paho-mqtt

import paho.mqtt.client as mqtt
import json

# Define MQTT settings
mqtt_broker = "test.mosquitto.org"  # Replace with your broker's IP address or hostname
mqtt_port = 1883  # Default port
mqtt_topic = "robot/tf"  # Topic to subscribe to

# This callback will be called when a message is received
def on_message(client, userdata, msg):
    # Decode message payload
    payload = msg.payload.decode('utf-8')
    data = json.loads(payload)
    
    # Print the frame data in Grasshopper
    print(f"Received message: {data}")
    
    # Here, you can extract specific values (e.g., translation, rotation) to use in Grasshopper
    translation = data['translation']
    rotation = data['rotation']
    
    # Pass this data to the Grasshopper output
    return translation, rotation

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the topic
    client.subscribe(mqtt_topic)

# Set up MQTT client
client = mqtt.Client()
client.on_message = on_message  # Set the callback function for received messages

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Subscribe to the topic
client.subscribe(mqtt_topic)

# Start the MQTT client loop to listen for messages
client.loop_forever()