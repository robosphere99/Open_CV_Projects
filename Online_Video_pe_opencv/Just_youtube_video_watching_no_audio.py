from yt_dlp import YoutubeDL
import cv2

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

# OpenCV Stream Processing
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream ended or cannot fetch frames")
        break

    # Display the frame
    cv2.imshow("YouTube Stream", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
