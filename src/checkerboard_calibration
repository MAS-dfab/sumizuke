import cv2
import numpy as np
import glob

# Define checkerboard size
CHECKERBOARD = (9, 6)  # (rows, cols) - adjust to your checkerboard
square_size = 0.024  # Size of a square in meters (25mm here)

# Arrays to store 3D points in real world and 2D points in image plane
obj_points = []  # 3D world points
img_points = []  # 2D image points

# Prepare the 3D coordinates of the checkerboard corners
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)
objp *= square_size  # Scale to real-world size

# Load images
image_files = glob.glob("captured_images/*.jpg")  # Update with your images path

for fname in image_files:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find checkerboard corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        obj_points.append(objp)
        img_points.append(corners)

        # Draw corners
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
        cv2.imshow('Checkerboard Detection', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Calibrate camera
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

# Save results
np.savez("camera_calibration_data.npz", camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)

print("\n=== Calibration Complete ===")
print("Camera Matrix:\n", camera_matrix)
print("Distortion Coefficients:\n", dist_coeffs)
print("RMS Error:", ret)
