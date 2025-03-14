import os
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import socket
import time

# NodeMCU Setup
nodemcu_ip = "192.168.29.5"  # Replace with your NodeMCU IP
nodemcu_port = 80

# Function to connect to NodeMCU
def connect_to_nodemcu():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((nodemcu_ip, nodemcu_port))
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("Connected to NodeMCU")
            return client_socket
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 2 seconds...")
            time.sleep(2)

# Initial connection
client_socket = connect_to_nodemcu()

# Setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread(r"C:\Users\anila\OneDrive\Documents\OpeenCV_Automation\Control_Home\Screens\BG.png")
disp = np.copy(imgBackground)
h, w = 300, 300  # Appliance image size
selectionSpeed = 7  # Speed of ellipse animation
applianceStates = [0, 0, 0, 0]  # 0=Off, 1=On for each appliance
counter = 0
selectedAppliance = -1
counterPause = 0
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Load appliance icons
folderPathIcons = r"C:\Users\anila\OneDrive\Documents\OpeenCV_Automation\Control_Home\Icons"
listImgIconsPath = os.listdir(folderPathIcons)
listImgIcons = [cv2.imread(os.path.join(folderPathIcons, imgPath)) for imgPath in listImgIconsPath]

# Appliance positions
positions = [(150, 730), (150, 980), (400, 730), (400, 980)]

while True:
    success, img = cap.read()
    img = cv2.resize(img, (662, 470))
    hands, img = detector.findHands(img)  # Detect hands
    imgBackground[188:188 + 470, 54:54 + 662] = img  # Overlay webcam feed

    # Draw appliances on the background
    for i, (y, x) in enumerate(positions):
        iconIndex = i * 2 + applianceStates[i]
        imgBackground[y:y + h, x:x + w] = listImgIcons[iconIndex]

    # Process hand gestures
    if hands and counterPause == 0:
        hand1 = hands[0]
        fingers1 = detector.fingersUp(hand1)

        # Map gestures to appliances
        if fingers1 == [0, 1, 0, 0, 0]:
            if selectedAppliance != 0:
                counter = 1
                selectedAppliance = 0
        elif fingers1 == [0, 1, 1, 0, 0]:
            if selectedAppliance != 1:
                counter = 1
                selectedAppliance = 1
        elif fingers1 == [0, 1, 1, 1, 0]:
            if selectedAppliance != 2:
                counter = 1
                selectedAppliance = 2
        elif fingers1 == [0, 1, 1, 1, 1]:
            if selectedAppliance != 3:
                counter = 1
                selectedAppliance = 3

        # Animation for toggling appliance
        if counter > 0:
            counter += 1
            y, x = positions[selectedAppliance]
            cv2.ellipse(imgBackground, (x + w // 2, y + h // 2), (103, 103), 0, 0,
                        counter * selectionSpeed, (0, 255, 0), 20)
        if counter * selectionSpeed > 360:
            applianceStates[selectedAppliance] = 1 - applianceStates[selectedAppliance]  # Toggle state
            data = f"{applianceStates}\n"  # Send states as a list
            try:
                client_socket.sendall(data.encode())  # Send data
                print("Data sent:", data)
            except (socket.error, ConnectionResetError, ConnectionAbortedError):
                print("Connection lost. Reconnecting...")
                client_socket.close()  # Close the old socket
                client_socket = connect_to_nodemcu()  # Reconnect
            counter = 0
            selectedAppliance = -1
            counterPause = 1

    # Pause to avoid multiple toggles
    if counterPause > 0:
        counterPause += 1
        if counterPause > 60:
            counterPause = 0

    # Display
    cv2.imshow("Background", imgBackground)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

client_socket.close()
