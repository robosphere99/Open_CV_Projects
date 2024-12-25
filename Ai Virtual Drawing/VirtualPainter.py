import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

#######################
brushThickness = 25
eraserThickness = 100
########################

folderPath = r"C:\Users\anila\OneDrive\Documents\OpeenCV_Automation\Ai Virtual Drawing\Header"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
print(len(overlayList))
header = overlayList[0]
drawColor = (255, 0, 255)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.65, maxHands=1)
xp, yp = 0, 0  # Previous x, y position (for drawing)
imgCanvas = np.zeros((720, 1280, 3), np.uint8)  # Blank canvas to draw on

while True:
    # 1. Import image
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip the image horizontally for a mirror effect

    # 2. Find Hand Landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Tip of index and middle fingers
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. If Selection Mode - Two fingers are up
        if fingers[1] and fingers[2]:
            print("Selection Mode")
            # Checking for the click to change the color
            if y1 < 125:
                if 250 < x1 < 450:
                    header = overlayList[0]
                    drawColor = (0, 0, 255)
                elif 550 < x1 < 750:
                    header = overlayList[1]
                    drawColor = (0, 255, 0)
                elif 800 < x1 < 950:
                    header = overlayList[2]
                    drawColor = (255, 0, 0)
                elif 1050 < x1 < 1200:
                    header = overlayList[3]
                    drawColor = (0, 0, 0)

            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            # Reset xp, yp when fingers are in selection mode (pen is "up")
            xp, yp = 0, 0

        # 5. If Drawing Mode - Index finger is up (and middle finger down)
        if fingers[1] and not fingers[2]:  # Drawing mode
            print("Drawing Mode")
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)  # Visualize the current touch point
            if xp == 0 and yp == 0:  # First time drawing
                xp, yp = x1, y1

            # Draw on canvas only when moving from the previous point (only if pen is down)
            cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)  # Update the canvas with new line
            xp, yp = x1, y1  # Save the current position for the next frame

        # 6. If all fingers are down (pen lift)
        if not any(fingers):
            xp, yp = 0, 0  # Reset the previous position when pen is lifted

    # Create the inverted image to combine with the frame
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    # Combine the current frame with the drawn canvas
    img = cv2.bitwise_and(img, imgInv)  # Show only the non-drawn parts from the camera frame
    img = cv2.bitwise_or(img, imgCanvas)  # Show the drawing from the canvas

    # Display the header image
    img[0:125, 0:1280] = header

    # Show the final images
    cv2.imshow("Image", img)  # The camera feed with drawing overlay
    cv2.imshow("Canvas", imgCanvas)  # Just the canvas with drawings
    cv2.waitKey(1)
