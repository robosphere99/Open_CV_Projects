import cv2
from fer import FER

# Initialize the webcam and FER detector
cap = cv2.VideoCapture(0)  # 0 is the default camera
detector = FER()

# Function to detect emotions from webcam feed
def detect_emotions(frame):
    # Detect emotions on the current frame
    result = detector.detect_emotions(frame)
    if result:
        # Extract emotions and their scores
        for person in result:
            emotions = person['emotions']
            # Find the dominant emotion
            dominant_emotion = max(emotions, key=emotions.get)
            return dominant_emotion, emotions[dominant_emotion]
    return None, None

# Loop through each frame from the webcam
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect emotions
    dominant_emotion, confidence = detect_emotions(frame)

    if dominant_emotion:
        # Display the emotion and confidence score on the frame
        text = f"Emotion: {dominant_emotion} ({confidence:.2f})"
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Show the frame with emotion detection
    cv2.imshow("Face Expression Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
