from yt_dlp import YoutubeDL
import cv2
import mediapipe as mp

# YouTube video link
youtube_url = "https://www.youtube.com/watch?v=hxMNYkLN7tI"

# Get the best video stream URL
def get_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[ext=mp4]',  # Choose best quality in mp4 format
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

# Fetch the direct stream URL
stream_url = get_stream_url(youtube_url)
print("Direct Stream URL:", stream_url)

# OpenCV Stream Processing for video
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream ended or cannot fetch frames")
        break

    # Convert the frame to RGB for Mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform pose detection
    results = pose.process(rgb_frame)

    # Draw pose landmarks on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display the frame with detections
    cv2.imshow("Person Detection with Mediapipe", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
