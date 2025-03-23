import os
import shutil
import random

# Paths to your dataset folder
dataset_path = "C:/Users/akango/Downloads/data"  # Change this to your actual dataset path

# Parent folder /dataset for output
output_path = os.path.join(os.path.dirname(__file__), "..", "dataset")

# Train/val split ratio
train_ratio = 0.8  # 80% training, 20% validation

# Create output directories
train_images_dir = os.path.join(output_path, "images/train")
train_labels_dir = os.path.join(output_path, "labels/train")
val_images_dir = os.path.join(output_path, "images/val")
val_labels_dir = os.path.join(output_path, "labels/val")

if not os.path.exists(train_images_dir):
    os.makedirs(train_images_dir)
if not os.path.exists(train_labels_dir):
    os.makedirs(train_labels_dir)
if not os.path.exists(val_images_dir):
    os.makedirs(val_images_dir)
if not os.path.exists(val_labels_dir):
    os.makedirs(val_labels_dir)

# Get all image files (assuming all labels have corresponding images)
image_files = [f for f in os.listdir(dataset_path) if f.endswith(".jpg")]
random.shuffle(image_files)  # Shuffle for randomness

# Split dataset
split_index = int(len(image_files) * train_ratio)
train_files = image_files[:split_index]
val_files = image_files[split_index:]

# Function to move files
def move_files(file_list, src_folder, dest_images, dest_labels):
    for img_file in file_list:
        txt_file = img_file.replace(".jpg", ".txt")
        
        # Source paths
        img_src = os.path.join(src_folder, img_file)
        txt_src = os.path.join(src_folder, txt_file)
        
        # Destination paths
        img_dest = os.path.join(dest_images, img_file)
        txt_dest = os.path.join(dest_labels, txt_file)

        # Move files if they exist
        if os.path.exists(img_src):
            shutil.copy(img_src, img_dest)
        if os.path.exists(txt_src):
            shutil.copy(txt_src, txt_dest)

# Move train and validation files
move_files(train_files, dataset_path, train_images_dir, train_labels_dir)
move_files(val_files, dataset_path, val_images_dir, val_labels_dir)

print(f"Dataset split completed! Train: {len(train_files)}, Val: {len(val_files)}")
