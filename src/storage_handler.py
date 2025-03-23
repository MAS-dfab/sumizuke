import paho.mqtt.client as mqtt
from pymongo import MongoClient
import datetime, sys

import threading

TCP_TOPIC = "craftsx/tcp"
TF_TOPIC = "craftsx/tf"
MQTT_SERVER = "test.mosquitto.org"

# Global variable to store tf data
tf_data = None
tf_lock = threading.Lock()

# Replace with your actual MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://roboto:Sumizuke@craftsx.vbq9e.mongodb.net/?retryWrites=true&w=majority&appName=craftsx"
# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Select a database and collection
db = client["robot_db"]  # Database
align_collection = db["alignment_points"]  # Collection (like a table in SQL)
design_collection = db["design_points"]  # Collection (like a table in SQL)

module_path = "../utils"
sys.path.append(module_path)

if module_path not in sys.path:
    sys.path.append(module_path)

from pymongo_utils import insert_data, fetch_data, delete_data, check_collection_size

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", str(rc))
    client.subscribe(TCP_TOPIC)

def update_tf():
    """ Continuously listens for tf updates in a separate thread. """
    def on_tf_message(client, userdata, msg):
        global tf_data
        try:
            new_tf = msg.payload.decode()
            with tf_lock:
                tf_data = new_tf
            print(f"TF Data Updated: {tf_data}")
        except Exception as e:
            print("Error processing TF message:", e)
    
    tf_client = mqtt.Client()
    tf_client.on_connect = lambda c, u, f, r: c.subscribe(TF_TOPIC)
    tf_client.on_message = on_tf_message
    tf_client.connect(MQTT_SERVER, 1883, 60)
    tf_client.loop_forever()

def on_message_tcp(client, userdata, msg):
    """ Callback function for handling TCP messages. """
    try:
        data = msg.payload.decode()
        mode, id = data.split(",")
        point_data = {
            "id": id,
            "tf": tf_data,
            "timestamp": datetime.datetime.now()
        }
        # Insert the data into the collection
        if mode == "2":
            insert_data(align_collection, point_data)
        elif mode == "3":
            insert_data(design_collection, point_data)
        
    except Exception as e:
        print("Error processing TCP message:", e)


client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add(TCP_TOPIC, on_message_tcp)
client.connect(MQTT_SERVER, 1883, 60)

# Start TF listener in a separate thread
tf_thread = threading.Thread(target=update_tf, daemon=True)
tf_thread.start()

client.loop_forever()