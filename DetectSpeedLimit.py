import cv2
import os

import DetectChars
import DetectSigns


class DetectSpeedLimit:

    def __init__(self,frame, readFromImg=4):
        self.SCALAR_BLACK = (0.0, 0.0, 0.0)
        self.SCALER_WHITE = (255.0, 255.0, 255.0)
        self.SCALAR_YELLOW = (0.0, 255.0, 255.0)
        self.SCALAR_GREEN = (0.0, 255.0, 0.0)
        self.SCALAR_RED = (0.0, 0.0, 255.0)
        if readFromImg == 0:
            self.readFromStaticImage()
        # if readFromImg == 1:
            # self.readFromFrame(frame)

    def drawRedRectangleAroundSign(self, originalFrame, sign):
        p2fRectPoints = cv2.boxPoints(sign.rrLocationOfSignInFrame)
        cv2.line(originalFrame, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), self.SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), self.SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), self.SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), self.SCALAR_RED, 2)

    def writeSpeedLimitCharsOnImage(self, originalFrame, sign):
        fHeight, fWidth, fNumChannels = originalFrame.shape
        sHeight, sWidth, sNumChannels = sign.imgSign.shape

        intFontFace = cv2.FONT_HERSHEY_SIMPLEX
        fltFontScale = float(sHeight)/50
        intFontThickness = int(round(fltFontScale*2))

        textSize, baseline = cv2.getTextSize(sign.strChar, intFontFace, fltFontScale, intFontThickness)

        # get sign dimensions
        ((intSignCenterX, intSignCenterY), (intSignWidth, intSignHeight), fltCorrectAngleInDeg) \
            = sign.rrLocationOfSignInFrame

        # make sure center is an integer
        intSignCenterX = int(intSignCenterX)
        intSignCenterY = int(intSignCenterY)

        ptCenterOfTextAreaX = int(intSignCenterX)

        if intSignCenterY < (fHeight*0.75):
            # write the chars in below the Sign
            ptCenterOfTextAreaY = int(round(intSignCenterY)) + int(round(sHeight * 1.6))
        else:  # else if the license Sign is in the lower 1/4 of the image
            # write the chars in above the Sign
            ptCenterOfTextAreaY = int(round(intSignCenterY)) - int(round(sHeight * 1.6))

        textSizeWidth, textSizeHeight = textSize

        ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))
        # based on the text area center, width, and height
        ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))
        # write the text on the image
        cv2.putText(originalFrame, sign.strChar, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace,
                    fltFontScale, self.SCALAR_YELLOW, intFontThickness)

        return originalFrame

    def readFromStaticImage(self):
        blnkKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()

        if not blnkKNNTrainingSuccessful:
            print("\nError: KNN training was not successful\n")
            return

        imgOriginalFrame = cv2.imread("speed_limit_31.jpg")

        if imgOriginalFrame is None:
            print("\nError: image not read from file\n\n")
            os.system("pause")
            return

        listOfPossibleSigns = DetectSigns.detectSignsInScene(imgOriginalFrame)
        listOfPossibleSigns = DetectChars.detectCharsInSign(listOfPossibleSigns)

        cv2.imshow("imgOriginalFrame", imgOriginalFrame)

        if len(listOfPossibleSigns) == 0:
            print("\nNo speed limit signs were detected\n")
        else:
            listOfPossibleSigns.sort(key=lambda possibleSigns: 2, reverse=True)
            spdSign = listOfPossibleSigns[0]
            cv2.imshow("imgSign", spdSign.imgSign)
            cv2.imshow("imgThresh", spdSign.imgThresh)

            if len(spdSign.strChar) == 0:
                print("\nNo Characters Were Detected\n\n")
                return

            self.drawRedRectangleAroundSign(imgOriginalFrame, spdSign)

            print("\nSpeed Limit Read From Image: {0}\n".format(spdSign.strChar))
            print("------------------------------------")

            self.writeSpeedLimitCharsOnImage(imgOriginalFrame, spdSign)

            cv2.imshow("imgOriginalFrame", imgOriginalFrame)
            cv2.imwrite("imgOriginalFrame.png", imgOriginalFrame)

        cv2.waitKey(0)
        return

    def readVideo(self):
        blnkKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()

        if not blnkKNNTrainingSuccessful:
            print("\nError: KNN training was not successful\n")
            return

        _, video = cv2.VideoCapture(0)
        success, frame = video.read()
        self.readFromFrame(frame)
        imgOriginalFrame = cv2.imread("speed_limit_80.jpg")

        if imgOriginalFrame is None:
            print("\nError: image not read from file\n\n")
            os.system("pause")
            return
        self.readFromFrame(frame)
        cv2.waitKey(0)
        return

    def readFromFrame(self, sign, frame):
        listOfPossibleSigns = DetectSigns.detectSignsInScene(sign)
        print(listOfPossibleSigns)
        listOfPossibleSigns = DetectChars.detectCharsInSign(listOfPossibleSigns)

        # cv2.imshow("imgOriginalFrame", frame)

        if listOfPossibleSigns is None or len(listOfPossibleSigns) == 0:
            print("\nNo speed limit signs were detected\n")
            return frame
        else:
            listOfPossibleSigns.sort(key=lambda possibleSigns: 2, reverse=True)
            spdSign = listOfPossibleSigns[0]

            if len(spdSign.strChar) == 0:
                print("\nNo Characters Were Detected\n\n")
                return frame

            self.drawRedRectangleAroundSign(frame, spdSign)

            print("\nSpeed Limit Read From Image: {0}\n".format(spdSign.strChar))
            print("------------------------------------")

            return self.writeSpeedLimitCharsOnImage(frame, spdSign)

