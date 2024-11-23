import cv2
import numpy as np
import time
import pyautogui
import mediapipe as mp

# Configuration parameters
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

# Previous location of mouse cursor
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Webcam initialization
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Hand tracking initialization using MediaPipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

# Screen size (pyautogui provides this function)
wScr, hScr = pyautogui.size()

while True:
    # 1. Find hand landmarks
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]  # Get the first detected hand

        # Draw hand landmarks
        mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)

        # Get coordinates of landmarks
        lmList = []
        for id, lm in enumerate(hand.landmark):
            ih, iw, ic = img.shape
            x, y = int(lm.x * iw), int(lm.y * ih)
            lmList.append([id, x, y])

        # 2. Get the tip of the index and middle fingers
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]  # Index finger tip
            x2, y2 = lmList[12][1:] # Middle finger tip

            # 3. Check which fingers are up
            fingers = [
                int(lmList[i][2] < lmList[i - 1][2]) for i in [8, 12]  # Index and Middle fingers
            ]

            # Draw frame for action area
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

            # 4. Only index finger is up: Moving mode
            if fingers[0] == 1 and fingers[1] == 0:
                # 5. Convert coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # 6. Smooth the cursor movement
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move the mouse using pyautogui
                pyautogui.moveTo(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

            # 8. Both index and middle fingers are up: Clicking mode
            if fingers[0] == 1 and fingers[1] == 1:
                # 9. Find distance between fingers
                length = np.linalg.norm(np.array((x1, y1)) - np.array((x2, y2)))

                # 10. Click mouse if distance is short
                if length < 40:
                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0  # Prevent division by zero
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display the image
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
