from yt_dlp import YoutubeDL
import cv2
import mediapipe as mp
import vlc
import threading
import time

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

# Function to play audio using VLC
def play_audio(url):
    instance = vlc.Instance("--no-video")  # Disable video in VLC
    player = instance.media_player_new()
    media = instance.media_new(url)
    player.set_media(media)
    player.play()

    while player.is_playing():
        time.sleep(0.1)  # Keep thread alive as long as audio is playing

# Start audio playback in a separate thread
audio_thread = threading.Thread(target=play_audio, args=(stream_url,))
audio_thread.daemon = True
audio_thread.start()

# OpenCV Stream Processing for video
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Get the video frame rate (FPS) from the stream
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 FPS if not available
frame_delay = int(1000 / fps)  # Delay per frame in milliseconds

# Synchronize video with audio
start_time = time.time()  # Start time to sync video with audio

while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream ended or cannot fetch frames")
        break

    # Calculate the time difference to sync with audio playback
    elapsed_time = time.time() - start_time
    cap.set(cv2.CAP_PROP_POS_MSEC, elapsed_time * 1000)  # Set video position to sync with audio

    # Convert the frame to RGB for Mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform pose detection
    results = pose.process(rgb_frame)

    # Draw pose landmarks on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display the frame with detections
    cv2.imshow("Mediapipe Person Detection with Audio Sync", frame)

    # Check for 'q' to exit
    if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
