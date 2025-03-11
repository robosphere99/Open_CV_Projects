import cv2
import serial

esp32_serial = serial.Serial('COM4', 115200)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(2)

frame_width = 640
frame_height = 480

def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        center_x = x + w // 2
        center_y = y + h // 2

        # Reverse mapping to fix movement direction
        pan_angle = map_range(center_x, 0, frame_width, 180, 0)  # Reverse for pan
        tilt_angle = map_range(center_y, 0, frame_height, 0, 180)  # Reverse for tilt

        command = f"{pan_angle},{tilt_angle}\n"
        esp32_serial.write(command.encode())

    cv2.imshow('Face Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp32_serial.close()
