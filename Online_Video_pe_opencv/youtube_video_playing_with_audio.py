from yt_dlp import YoutubeDL
import cv2
import vlc
import threading
import time

# YouTube video link
youtube_url = "https://www.youtube.com/watch?v=cBGDDBHN22U"

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

# Function to play audio using VLC without showing video
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

# Get the video frame rate (FPS) from the stream
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 FPS if not available
frame_delay = int(1000 / fps)  # Delay per frame in milliseconds

while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream ended or cannot fetch frames")
        break

    # Display the frame
    cv2.imshow("YouTube Stream with Audio", frame)

    # Exit on 'q' key press
    if cv2.waitKey(frame_delay) & 0xFF == ord('q'):  # Use frame delay here
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
