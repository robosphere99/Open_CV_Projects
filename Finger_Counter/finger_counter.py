import cv2
import mediapipe as mp

# Initialize mediapipe's hand detection module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Function to detect raised fingers
def count_fingers(hand_landmarks):
    finger_tips_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Little fingertips

    fingers = []
    for i in range(1, 5):  # Check fingers other than thumb
        if hand_landmarks.landmark[finger_tips_ids[i]].y < hand_landmarks.landmark[finger_tips_ids[i] - 2].y:
            fingers.append(1)  # Finger is raised
        else:
            fingers.append(0)  # Finger is not raised

    # Check thumb separately
    if hand_landmarks.landmark[finger_tips_ids[0]].x < hand_landmarks.landmark[finger_tips_ids[0] - 1].x:
        fingers.append(1)  # Thumb is raised
    else:
        fingers.append(0)  # Thumb is not raised

    return fingers.count(1)  # Return count of raised fingers

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (as mediapipe requires RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hand landmarks
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count the raised fingers
            fingers_count = count_fingers(hand_landmarks)

            # Display the number of raised fingers
            cv2.putText(frame, f'Fingers: {fingers_count}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Finger Counter', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
