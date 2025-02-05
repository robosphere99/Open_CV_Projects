import cv2
import mediapipe as mp
import numpy as np

# Initialize mediapipe's hand detection module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Keyboard layout (a simple layout example)
keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']]

# Function to draw the virtual keyboard
def draw_keyboard(frame, keys):
    key_width = 70
    key_height = 70
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = j * key_width + 50
            y = i * key_height + 100
            cv2.rectangle(frame, (x, y), (x + key_width, y + key_height), (255, 255, 255), 3)
            cv2.putText(frame, key, (x + 20, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Function to detect fingertip and return which key is pressed
def detect_keypress(finger_tip_x, finger_tip_y, keys):
    key_width = 70
    key_height = 70
    col = (finger_tip_x - 50) // key_width
    row = (finger_tip_y - 100) // key_height

    if 0 <= row < len(keys) and 0 <= col < len(keys[row]):
        return keys[row][col]
    return None

# Initialize the webcam
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (for mediapipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hand landmarks
    result = hands.process(rgb_frame)

    # Draw virtual keyboard on the frame
    draw_keyboard(frame, keys)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get fingertip coordinates of the index finger (landmark 8)
            index_finger_tip = hand_landmarks.landmark[8]
            h, w, _ = frame.shape
            finger_tip_x = int(index_finger_tip.x * w)
            finger_tip_y = int(index_finger_tip.y * h)

            # Check if any key is pressed
            pressed_key = detect_keypress(finger_tip_x, finger_tip_y, keys)
            if pressed_key:
                cv2.putText(frame, f'Key: {pressed_key}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    # Display the frame
    cv2.imshow('AI Virtual Keyboard', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
