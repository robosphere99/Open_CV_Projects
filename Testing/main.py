import cv2

# Open video file or webcam feed
video_path = 0  # Use 0 for webcam, or replace with a video file path, e.g., 'video.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("End of video or no webcam feed.")
        break

    # Display the frame
    cv2.imshow("Video Feed", frame)

    # Press 'q' to exit
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()