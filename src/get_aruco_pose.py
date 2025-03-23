import cv2
import numpy as np

print(cv2.__version__)


import paho.mqtt.client as mqtt

# MQTT Broker Configuration
BROKER = "test.mosquitto.org"  # Public MQTT broker
TOPIC = "craftsx/img"  # Same topic as in Nicla Vision script


def get_aruco_marker_poses(img):
    """Detect ArUco markers in the image and return their poses."""
    # Define the dictionary of ArUco markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    aruco_params = cv2.aruco.DetectorParameters()
    # Detect the markers
    corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)

    # Camera calibration parameters (from checkerboard calibration)
    camera_matrix = np.array( [[ 412.5,   0.,         159.49918896],
 [  0.,          412.5, 159.49984471,],
 [  0.,           0.,           1.        ]], dtype=np.float32)
    
    dist_coeffs = np.array([[-0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 0.00000000e+00]], dtype=np.float32)

    # Estimate the pose of the markers
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.1, camera_matrix, dist_coeffs)

    # Construct the transformation matrices
    T_marker_camera = []
    for rvec, tvec in zip(rvecs, tvecs):
        R, _ = cv2.Rodrigues(rvec)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = tvec.squeeze()
        T_marker_camera.append(T)

    return T_marker_camera

def preprocess_image(img_bytes):
    """Convert received image bytes to a NumPy array and resize."""
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_resized = cv2.resize(img, (320, 320))  # Resize to 256x256
    return img

def on_message(client, userdata, message):
    """Callback function for MQTT message reception."""
    try:
        img_bytes = message.payload
        img = preprocess_image(img_bytes)

        # Display the image
        cv2.imshow("Nicla Vision", img)

        # Get the poses of the ArUco markers
        T_marker_camera = get_aruco_marker_poses(img)

        if len(T_marker_camera) == 0:
            print("No ArUco markers detected!")
        else:
            print("Detected ArUco markers:")
            print(T_marker_camera)


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

def euler_to_rotation_matrix(rx, ry, rz, degrees=True):
    """ Convert Euler angles (rx, ry, rz) to a 3x3 rotation matrix. """
    if degrees:
        rx, ry, rz = np.radians([rx, ry, rz])  # Convert to radians
    
    # Rotation matrices for X, Y, Z
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(rx), -np.sin(rx)],
                   [0, np.sin(rx), np.cos(rx)]])
    
    Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
                   [0, 1, 0],
                   [-np.sin(ry), 0, np.cos(ry)]])
    
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                   [np.sin(rz), np.cos(rz), 0],
                   [0, 0, 1]])
    
    # Combined rotation matrix: R = Rz * Ry * Rx (ZYX Euler convention)
    R = Rz @ Ry @ Rx
    return R

def xyz_rpy_to_transformation_matrix(x, y, z, rx, ry, rz, degrees=True):
    """ Convert XYZ position and Euler angles (RX, RY, RZ) into a 4x4 transformation matrix. """
    R = euler_to_rotation_matrix(rx, ry, rz, degrees)  # Get rotation matrix
    T = np.eye(4)  # Create identity matrix (4x4)
    T[:3, :3] = R  # Set rotation part
    T[:3, 3] = [x, y, z]  # Set translation part
    return T

T3 = xyz_rpy_to_transformation_matrix(-0.1870, -0.5468, 0.5562, 2.026, -2.15, -0.953, degrees=False)
T1 = xyz_rpy_to_transformation_matrix(-0.6448, -0.045, 0.5884, 0.293, -3.450, 0.355, degrees=False)
T2 = xyz_rpy_to_transformation_matrix(-0.5787, -0.0195, 0.504, 0.394, -3.250, 0.407, degrees=False)

print([T1, T2, T3])