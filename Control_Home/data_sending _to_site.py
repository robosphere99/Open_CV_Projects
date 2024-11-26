import os
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import requests
import threading  # For periodic refresh
import time
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

# API: Update single device status
def update_device_status(device_id, status):
    url = f"http://localhost/onlineswitch/api/update_device_status.php?api_key=752b167ae5fc91cd6715b7c0c9edbc8b&device_id={device_id}&status={status}"
    try:
        response = requests.get(url)
        print(f"Device {device_id} status updated to {status}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating device {device_id} status: {e}")

# API: Fetch all devices' statuses
def fetch_device_status():
    global applianceStates
    url = "http://localhost/onlineswitch/api/get_all_devices_status_using_api.php?api_key=752b167ae5fc91cd6715b7c0c9edbc8b"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            devices = response.json()
            for i, device in enumerate(devices):
                applianceStates[i] = 1 if device["status"] == "on" else 0
            print("Device states refreshed:", applianceStates)
        else:
            print("Failed to fetch device status")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device status: {e}")

# Periodic status refresh thread
def periodic_refresh():
    while True:
        fetch_device_status()
        # cv2.waitKey(5000)  # Refresh every 5 seconds
        time.sleep(5)
# Start periodic refresh in a separate thread
refresh_thread = threading.Thread(target=periodic_refresh, daemon=True)
refresh_thread.start()
print("Periodic refresh thread started")  # Debugging


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
            update_device_status(selectedAppliance + 1, "on" if applianceStates[selectedAppliance] else "off")  # Update API
            print("Data updated:", applianceStates)
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

cap.release()
cv2.destroyAllWindows()
