import cv2
import numpy as np

URL = "10.26.5.2:5802"

upper_blue = (106, 255, 255)
lower_blue = (99, 30, 30)
 
upper_green = (96, 255, 255)
lower_green = (70, 30,30)

upper_red = (180, 255, 255)
lower_red = (170, 150, 150)

upper_red2 = (5, 255, 255)
lower_red2 = (0, 150, 150)

upper_yellow = (40, 255, 255)
lower_yellow =( 25, 60, 100)

cap = cv2.VideoCapture(URL)
cap.set(cv2.CAP_PROP_EXPOSURE, -9.5) ## 9.5 is best

center = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2))

def getColor():

    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    isBlue = cv2.inRange(hsv, lower_blue, upper_blue)
    isGreen = cv2.inRange(hsv, lower_green, upper_green)
    isRed = cv2.inRange(hsv, lower_red, upper_red)
    isRed2 = cv2.inRange(hsv, lower_red2, upper_red2)
    isYellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    if (cv2.waitKey(1) & 0xFF == ord("q")):
        val = None
        if (isBlue[center[1]][center[0]]):
            val = "blue"
        elif (isGreen[center[1]][center[0]]):
            val = "green"
        elif (isRed[center[1]][center[0]]) or (isRed2[center[1]][center[0]]):
            val = "red"
        elif (isYellow[center[1]][center[0]]):
            val = "yellow"
        return val
