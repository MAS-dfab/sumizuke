import cv2
import numpy as np


# Data: Robot base to TCP transformations
T_robot_base = [np.array([[-0.89340665, -0.25057265,  0.37287786, -0.6448    ],
       [-0.33119043,  0.92815905, -0.16980484, -0.045     ],
       [-0.30354151, -0.27519836, -0.91221073,  0.5884    ],
       [ 0.        ,  0.        ,  0.        ,  1.        ]]), 
       
       np.array([[-0.91292173, -0.32738439,  0.24370756, -0.5787    ],
       [-0.39353237,  0.86439394, -0.31297826, -0.0195    ],
       [-0.10819513, -0.38163147, -0.91796037,  0.504     ],
       [ 0.        ,  0.        ,  0.        ,  1.        ]]), 
       
       np.array([[-0.31705158, -0.79378237, -0.51902586, -0.187     ],
       [ 0.44618237,  0.35807581, -0.82018474, -0.5468    ],
       [ 0.83689879, -0.49162106,  0.2406432 ,  0.5562    ],
       [ 0.        ,  0.        ,  0.        ,  1.        ]])]

# Data: Camera to Marker transformations (from OpenMV ArUco detection)
T_marker_camera = [np.array([[-0.94046185, -0.31043569, -0.13842395,  0.01754837],
       [-0.1033074 ,  0.64904612, -0.753702  ,  0.01772238],
       [ 0.32381954, -0.69452776, -0.64247342,  0.25247024],
       [ 0.        ,  0.        ,  0.        ,  1.        ]]),

    np.array([[-0.88494201, -0.34326898, -0.31471265,  0.08255002],
       [ 0.01137001,  0.65965526, -0.75148231,  0.04938815],
       [ 0.46556242, -0.66859655, -0.57985368,  0.30340641],
       [ 0.        ,  0.        ,  0.        ,  1.        ]]),

    np.array([[-0.14461501, -0.97396515, -0.17458059, -0.03030174],
       [-0.86182727,  0.03729628,  0.50582877,  0.07044651],
       [-0.48614839,  0.22360875, -0.84478333,  0.34658038],
       [ 0.        ,  0.        ,  0.        ,  1.        ]])]

# Run the hand-eye calibration to get camera to robot transformation
R_cam_robot, t_cam_robot = cv2.calibrateHandEye(
    R_gripper2base=[T[:3, :3] for T in T_robot_base],   # Robot rotation part
    t_gripper2base=[T[:3, 3] for T in T_robot_base],    # Robot translation part
    R_target2cam=[T[:3, :3] for T in T_marker_camera],  # Marker rotation part
    t_target2cam=[T[:3, 3] for T in T_marker_camera],   # Marker translation part
    method=cv2.CALIB_HAND_EYE_TSAI  # Calibration method
)

print(R_cam_robot, t_cam_robot)
# Construct the final transformation matrix
T_cam_robot = np.eye(4)
T_cam_robot[:3, :3] = R_cam_robot.flatten().reshape(3, 3)
T_cam_robot[:3, 3] = t_cam_robot.ravel()

print("Final Camera-to-Robot Transformation Matrix:")
print(T_cam_robot)
