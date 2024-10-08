import os
import torch
from PIL import Image
import numpy as np
import json
import utils_dir.data_mapping as data_mapping
import utils_dir.visualization as visualization
from utils_dir.paths import *

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to load the model
def load_model():
    return torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5l.pt')

# Function to process the image and get bounding boxes
def process_image(model, image_path):
    image = Image.open(image_path)
    image_np = np.array(image)
    results = model(image)
    boxes = results.xyxy[0].cpu().numpy()  # Bounding boxes in the format [x1, y1, x2, y2, conf, cls]
    return image_np, boxes

# Function to save object images and metadata
def save_object_images(image_np, boxes, master_id):
    metadata = []
    for i, box in enumerate(boxes):
        x1, y1, x2, y2, conf, cls = box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Extract object from image
        object_image = image_np[y1-10:y2+10, x1-10:x2+10]
        object_image_pil = Image.fromarray(object_image)
        
        # Generate unique ID for the object
        unique_id = f'{master_id}_{i}'
        
        # Save object image
        object_image_path = os.path.join(SEGMENTED_OBJECTS_DIR, f'{unique_id}.jpg')
        object_image_pil.save(object_image_path)
        
        # Append metadata
        metadata.append({
            'unique_id': unique_id,
            'master_id': master_id,
            'image_path': object_image_path,
            'bbox': [x1, y1, x2, y2],
            'confidence': float(conf),
            'class': int(cls)
        })
    
    # Save metadata to a JSON file
    with open(METADATA_FILE, 'a') as f:
        for entry in metadata:
            f.write(json.dumps(entry) + '\n')

# Function to fetch all images of a given master image
def fetch_images_by_master_id(master_id):
    with open(METADATA_FILE, 'r') as f:
        metadata = [json.loads(line) for line in f]
    
    # Filter by master_id and return image paths
    return [entry['image_path'] for entry in metadata if entry['master_id'] == master_id]

# Main function
def image_segmentation():
    image_path = INPUT_IMAGE_FILE
    master_id = os.path.basename(image_path).split('.')[0]
    image = Image.open(image_path)

    # Load model and process image
    model = load_model()
    image_np, boxes = process_image(model, image_path)

    visualization.visualize_results(image, boxes, OUTPUT_DIR)
    
    # Save object images and metadata
    save_object_images(image_np, boxes, master_id)
    
    # Example usage: Fetch all images for the given master ID
    object_images = fetch_images_by_master_id(master_id)
    print(f'Fetched {len(object_images)} images for master ID {master_id}')

    


