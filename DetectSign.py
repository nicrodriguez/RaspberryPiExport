import cv2
import imutils
import numpy as np
import time

from DetectSpeedLimit import *


class DetectSign:
    def __init__(self, frame):
        self.frame = frame
        self.cropFrame = None
        self.DSL = DetectSpeedLimit(frame, 1)

        # self.gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    def preProcessFrame(self):
        ratio = self.frame.shape[0]/300.0
        orig = self.frame.copy()
        self.frame = imutils.resize(self.frame, height=300)
        # convert the image to grayscale, blur it, and find edges
        gray = cv2. cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        self.edged = cv2.Canny(gray, 30, 200)
        # cv2.imshow("edge", self.edged)
        # cv2.imshow("edged", edged)

    def findRectangle(self):
        self.preProcessFrame()
        (im2, cnts, _) = cv2.findContours(self.edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
        screenCnt = None

        if cnts is not None:
            # loop over our contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                mask = np.zeros((self.frame.shape[0], self.frame.shape[1]))
                out = np.zeros_like(self.frame)
                # if our approximated contour has four points, then
                # we can assume that we have found our screen
                if len(approx) == 4:
                    screenCnt = approx
                    p1 = screenCnt[0][0]
                    p2 = screenCnt[1][0]
                    p3 = screenCnt[2][0]
                    p4 = screenCnt[3][0]

                    if 600/750 - 0.2 < abs((p2[0] - p1[0])/(p3[1] - p1[1] + 0.001)) < 600/750 + 0.2:
                        # print((p2[0] - p1[0])/(p3[1] - p1[1]))
                        cv2.drawContours(self.frame, [screenCnt], -1, (0, 255, 0), 3)
                        cv2.fillConvexPoly(mask, screenCnt, 1)
                        mask = mask.astype(np.bool)
                        self.cropFrame = self.frame[p1[1]:p3[1], p1[0]:p2[0]]
                        # print(out)
                        # if out.size > 0:
                        #     cv2.imshow("Sign", out)
                        #     self.frame = self.DSL.readFromFrame(out, self.frame)
                        #     time.sleep(0.01)

        return self.frame


# frame = cv2.VideoCapture(0)
# while True:
#     _, screen_cap = frame.read()
#     altImg = DetectSign(screen_cap).findRectangle()
#     cv2.imshow("Blah", altImg)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# screen_cap.release()
# cv2.destroyAllWindows()
