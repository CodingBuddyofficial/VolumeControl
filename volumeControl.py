import time
import math
import cv2
import numpy

import handtrackingmodule as htm
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

###########################
wCam, hCam = 680, 450
###########################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75)
pTime = 0
vol=0
volBar=400
volPer=0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # Hand range 20 - 132
        # vol range -64 - 0
        vol = numpy.interp(length, [20, 100], [minVol, maxVol])
        volBar = numpy.interp(length, [20, 100], [400, 150])
        volPer = numpy.interp(length, [20, 100], [0, 100])
        print(int(length), vol)

        volume.SetMasterVolumeLevel(vol, None)
        if length < 20:
            cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f"{int(volPer)}%", (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    if 90 < int(volPer) <= 100:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "Max Volume", (400, 28), cv2.FONT_ITALIC, 1, (0, 0,255), 2)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
    if int(volPer) < 30:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0,255, 255), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS:-{int(fps)}", (20, 28), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
