import os

import cvzone
import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(r"C:\Users\anila\OneDrive\Documents\Jarvis\Try_shirt\Resources\Videos\1.mp4")
detector = PoseDetector()

shirtFolderPath = r"C:\Users\anila\OneDrive\Documents\Jarvis\Try_shirt\Resources\Shirts"
listShirts = os.listdir(shirtFolderPath)
print(listShirts)
fixedRatio = 262 / 190  # widthOfShirt/widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440
imageNumber = 0
imgButtonRight = cv2.imread(r"C:\Users\anila\OneDrive\Documents\Jarvis\Try_shirt\Resources\button.png", cv2.IMREAD_UNCHANGED)
if imgButtonRight is None:
    print("Error: Right button image not loaded.")
    exit()
else:
    print("Right button image loaded successfully.")
    # cv2.imshow("Loaded Button", imgButtonRight)
imgButtonLeft = cv2.flip(imgButtonRight, 1)
counterRight = 0
counterLeft = 0
selectionSpeed = 10

while True:
    success, img = cap.read()
    img = detector.findPose(img)
    img = cv2.flip(img,1)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=True, draw=True)
    if lmList:
        if lmList:
            # center = bboxInfo["center"]
            lm11 = lmList[11][1:3]
            lm12 = lmList[12][1:3]
            print(f"lm11: {lmList[11]}, lm12: {lmList[12]}")

            # Highlight and label landmarks 11 and 12
            for idx in [11, 12]:  # Landmarks to track
                x, y = lmList[idx][1], lmList[idx][2]
                cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)  # Red circle
                cv2.putText(img, f"{idx}: ({x}, {y})", (x + 20, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)  # Blue text

            imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[imageNumber]), cv2.IMREAD_UNCHANGED)

            widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)

        # print(widthOfShirt)
        # imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
        # Check if widthOfShirt is valid
    if widthOfShirt > 0:
        imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
    else:
        print(f"Invalid width calculated: {widthOfShirt}. Skipping this frame.")
        continue

        currentScale = (lm11[0] - lm12[0]) / 190
        offset = int(44 * currentScale), int(48 * currentScale)

        try:
            img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            # img = cvzone.overlayPNG(img, imgShirt, (100,100))
        except:
            pass

    img = cvzone.overlayPNG(img, imgButtonRight, (1072, 293))
    # cv2.imshow("button", imgButtonRight)
    img = cvzone.overlayPNG(img, imgButtonLeft, (72, 293))

    if lmList[16][1] < 300:
            counterRight += 1
            cv2.ellipse(img, (139, 360), (66, 66), 0, 0,
                        counterRight * selectionSpeed, (0, 255, 0), 20)
            if counterRight * selectionSpeed > 360:
                counterRight = 0
                if imageNumber < len(listShirts) - 1:
                    imageNumber += 1
    elif lmList[15][1] > 900:
            counterLeft += 1
            cv2.ellipse(img, (1138, 360), (66, 66), 0, 0,
                        counterLeft * selectionSpeed, (0, 255, 0), 20)
            if counterLeft * selectionSpeed > 360:
                counterLeft = 0
                if imageNumber > 0:
                    imageNumber -= 1

    else:
            counterRight = 0
            counterLeft = 0

    cv2.imshow("Image", img)
    cv2.waitKey(1)