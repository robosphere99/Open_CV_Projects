import cv2
import mediapipe as mp

# Initialize MediaPipe Pose model
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Initialize variables for counting
correct_count = 0
previous_position = None

# Function to check if the lift is correct
def is_correct_lift(landmarks):
    global previous_position

    # Extract relevant landmarks for shoulder and wrist
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    
    # Check for vertical alignment of wrist and shoulder for left hand
    if left_wrist.y < left_shoulder.y:
        lift_position = 'up'
    else:
        lift_position = 'down'

    # Counting logic
    if lift_position == 'up' and (previous_position != 'up'):
        previous_position = lift_position
        return True
    elif lift_position == 'down' and (previous_position == 'up'):
        previous_position = lift_position

    return False

# Initialize webcam feed
cap = cv2.VideoCapture(0)

# Set up the pose tracking model
with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Flip the frame horizontally and convert to RGB for processing
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect poses
        results = pose.process(rgb_frame)

        # Convert the frame back to BGR for OpenCV rendering
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Draw landmarks and check for correct lift
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            if is_correct_lift(results.pose_landmarks.landmark):
                correct_count += 1
            
            # Display the count
            cv2.putText(frame, f'Correct Lifts: {correct_count}', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        # Display the frame
        cv2.imshow('Exercise Form Tracker', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
