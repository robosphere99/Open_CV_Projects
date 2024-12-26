import cv2
import mediapipe as mp
import os
import numpy as np

# Initialize Mediapipe for Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmenter = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)  # model_selection=1 is the segmentation model
mp_drawing = mp.solutions.drawing_utils

# Directory containing background images
background_folder = r"C:\Users\anila\OneDrive\Documents\OpeenCV_Automation\Background_like_zoom\backgrounds\\"  # Replace with your actual path to the background images

# Get a list of all background images from the folder
background_images = [f for f in os.listdir(background_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
backgrounds = [cv2.imread(os.path.join(background_folder, img)) for img in background_images]
print("Background images found:", background_images)  # List the images being loaded
current_background_index = 0  # Default to first background

# Open webcam or video stream
cap = cv2.VideoCapture(0)  # Use the camera (0) or replace with video file if needed

if not cap.isOpened():
    print("Error: Unable to open webcam")
    exit()

# Get webcam dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Resize backgrounds to fit the frame dimensions
backgrounds = [cv2.resize(bg, (frame_width, frame_height)) for bg in backgrounds]

# Function to change background
def change_background(direction):
    global current_background_index
    if direction == 'next':
        current_background_index = (current_background_index + 1) % len(backgrounds)
    elif direction == 'previous':
        current_background_index = (current_background_index - 1) % len(backgrounds)

# Initialize background type
background_type = 'real'  # Default to real-time background (user visible)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to fetch frame")
        break

    # Convert the frame to RGB (required by Mediapipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame for segmentation
    results = segmenter.process(rgb_frame)

    # If segmentation mask is available, apply it
    if results.segmentation_mask is not None:
        # Convert the mask to a binary image
        mask = results.segmentation_mask
        
        # Convert the mask from float32 to uint8 (0 or 255) and resize it to match the frame dimensions
        mask = np.array(mask * 255, dtype=np.uint8)  # Convert to 8-bit mask
        mask = cv2.resize(mask, (frame_width, frame_height))  # Ensure mask is the same size as the frame
        
        # Apply the mask to separate the person from the background
        mask_3ch = np.stack([mask] * 3, axis=-1)  # Convert single-channel mask to 3 channels
        
        # Resize the background to match frame dimensions
        background = backgrounds[current_background_index]
        
        # Use the mask to combine the person and background
        person = cv2.bitwise_and(frame, frame, mask=mask)
        inverted_mask = cv2.bitwise_not(mask)
        bg = cv2.bitwise_and(background, background, mask=inverted_mask)
        
        # Combine the person and background
        final_frame = cv2.add(person, bg)
        
    else:
        final_frame = frame  # If segmentation fails, show original frame

    # Show the final frame with the background replaced
    cv2.imshow("Zoom-like System - Background Replacement", final_frame)

    key = cv2.waitKey(1) & 0xFF

    # Control key events
    if key == ord('n'):  # Next background
        change_background('next')
    elif key == ord('p'):  # Previous background
        change_background('previous')
    elif key == ord('r'):  # Real background (real-time)
        background_type = 'real'
    elif key == ord('q'):  # Quit
        break

# Release and close
cap.release()
cv2.destroyAllWindows()
