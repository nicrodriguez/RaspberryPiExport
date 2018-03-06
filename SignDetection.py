import cv2
import imutils
import numpy as np
import math
import os

KNearest = cv2.ml.KNearest_create()
# constants for checkIfPossibleChar, this checks one possible char only (does not compare to another char)
MIN_PIXEL_WIDTH = 2
MIN_PIXEL_HEIGHT = 8

MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0

MIN_PIXEL_AREA = 200

# constants for comparing two chars
MIN_DIAG_SIZE_MULTIPLE_AWAY = 0.3
MAX_DIAG_SIZE_MULTIPLE_AWAY = 5.0

MAX_CHANGE_IN_AREA = 0.5

MAX_CHANGE_IN_WIDTH = 0.8
MAX_CHANGE_IN_HEIGHT = 0.2

MAX_ANGLE_BETWEEN_CHARS = 12.0

# other constants
MIN_NUMBER_OF_MATCHING_CHARS = 2

RESIZED_CHAR_IMAGE_WIDTH = 20
RESIZED_CHAR_IMAGE_HEIGHT = 30

MIN_CONTOUR_AREA = 100

GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
ADAPTIVE_THRESH_BLOCK_SIZE = 21
ADAPTIVE_THRESH_WEIGHT = 2

SIGN_WIDTH_PADDING_FACTOR = 1.3
SIGN_HEIGHT_PADDING_FACTOR = 1.5

SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALER_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)


# Loading in training classifications and training data at start to increase runtime speed
def loadKNNDataAndTrainKNN():
    try:
        npaClassifications = np.loadtxt("classification_files/classifications.txt", np.float32)
    except:
        print("Error, unable to open classifications.txt, exiting program\n")
        return False

    try:
        npaFlattenedImages = np.loadtxt("classification_files/flattened_images.txt", np.float32)
    except:
        print("Error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return False

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    KNearest.setDefaultK(1)
    KNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    return True


blnkKNNTrainingSuccessful = loadKNNDataAndTrainKNN()


class DetectSign:
    def __init__(self, frame):
        self.frame = frame
        self.croppedFrame = None
        self.edged = None

    def processFrame(self):
        self.frame = imutils.resize(self.frame, height=300)
        # convert the image to grayscale, blur it, and find edges
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        gray = maximizeContrast(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        self.edged = cv2.Canny(gray, 40, 100)

    def findRectangle(self):
        self.processFrame()
        (im2, cnts, _) = cv2.findContours(self.edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

        if cnts is not None:
            # loop over our contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                # mask = np.zeros((self.frame.shape[0], self.frame.shape[1]))
                # out = np.zeros_like(self.frame)
                # if our approximated contour has four points, then
                # we can assume that we have found our screen
                if len(approx) == 4:
                    screenCnt = approx
                    p1 = screenCnt[0][0]
                    p2 = screenCnt[1][0]
                    p3 = screenCnt[2][0]
                    p4 = screenCnt[3][0]
                    if abs((p2[0] - p1[0])) == abs((p3[0] - p4[0])):
                        if 600 / 750 - 0.2 < abs((p2[0] - p1[0]) / (p3[1] - p1[1] + 0.001)) < 600 / 750 + 0.2:
                            # print((p2[0] - p1[0])/(p3[1] - p1[1]))
                            # cv2.fillConvexPoly(mask, screenCnt, 1)
                            cv2.drawContours(self.frame, [screenCnt], -1, SCALAR_GREEN, 1)
                            self.croppedFrame = self.frame[p1[1]:p3[1], p1[0]:p2[0]]

        return self.frame


class DetectSpeedLimit:
    def __init__(self, sign):
        self.readSpeedLimit = None

        self.sign = sign

        if not blnkKNNTrainingSuccessful:
            print("\nError: KNN training was not successful\n")
            return
        print('Reading Speed Limit')

    def drawRedRectangleAroundSign(self, originalFrame, sign):
        p2fRectPoints = cv2.boxPoints(sign.rrLocationOfSignInFrame)
        cv2.line(originalFrame, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
        cv2.line(originalFrame, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
        return originalFrame

    def readFromFrame(self, sign, frame):
        listOfPossibleSigns = detectSignsInScene(sign)
        print(listOfPossibleSigns)
        listOfPossibleSigns = detectCharsInSign(listOfPossibleSigns)

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

            frame = self.drawRedRectangleAroundSign(frame, spdSign)

            speedLimit = int(spdSign.strChar)  # int(5 * round(float() / 5))
            if speedLimit <= 100 and speedLimit % 5 == 0:
                self.readSpeedLimit = str(speedLimit)
                print("\nSpeed Limit Read From Image: {0}\n".format(spdSign.strChar))
                print("------------------------------------")

            return frame


class PossibleChar:

    def __init__(self, _contour):
        self.contour = _contour

        self.boundingRect = cv2.boundingRect(self.contour)

        [intX, intY, intWidth, intHeight] = self.boundingRect  # Obtains the dimensions of the rectangle

        self.intBoundingRectX = intX
        self.intBoundingRectY = intY
        self.intBoundingRectWidth = intWidth
        self.intBoundingRectHeight = intHeight

        self.intBoundingRectArea = self.intBoundingRectWidth * self.intBoundingRectHeight

        self.intCenterX = (2 * self.intBoundingRectX + self.intBoundingRectWidth) / 2
        self.intCenterY = (2 * self.intBoundingRectY + self.intBoundingRectHeight) / 2

        self.fltDiagonalSize = math.sqrt(self.intBoundingRectWidth ** 2 + self.intBoundingRectHeight ** 2)

        self.flatAspectRatio = float(self.intBoundingRectWidth) / float(self.intBoundingRectHeight)


class PossibleSign:

    def __init__(self):
        self.imgSign = None
        self.imgGray = None
        self.imgThresh = None

        self.rrLocationOfSignInFrame = None

        self.strChar = ""


def maximizeContrast(imgGray):
    # height, width = imgGray.shape
    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imgTopHat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, structuringElement)
    imgBlackHat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, structuringElement)

    imgGrayscalePlusTopHat = cv2.add(imgGray, imgTopHat)
    imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

    return imgGrayscalePlusTopHatMinusBlackHat




def detectCharsInSign(listOfPossibleSigns):
    if len(listOfPossibleSigns) == 0:
        return listOfPossibleSigns

    for possibleSign in listOfPossibleSigns:
        possibleSign.imgGray, possibleSign.imgThresh = preprocess(possibleSign.imgSign)

        # increase image size for easier viewing and char detection
        possibleSign.imgThresh = cv2.resize(possibleSign.imgThresh, (0, 0), fx=1.6, fy=1.6)

        # threshold again to eliminate any gray areas
        thresholdValue, possibleSign.imgThresh = cv2.threshold(possibleSign.imgThresh, 0.0, 255.0,
                                                               cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        listOfPossibleCharsInSigns = findPossibleCharsInSign(possibleSign.imgThresh)

        listOfListsOfMatchingCharsInSign = findListOfListsOfMatchingChars(listOfPossibleCharsInSigns)

        if len(listOfListsOfMatchingCharsInSign) == 0:
            possibleSign.strChar = ""
            continue

        for i in range(0, len(listOfListsOfMatchingCharsInSign)):
            listOfListsOfMatchingCharsInSign[i].sort(key=lambda matchingChar: matchingChar.intCenterX)
            listOfListsOfMatchingCharsInSign[i] = removeInnerOverlappingChars(listOfListsOfMatchingCharsInSign[i])

        intLenOfLongestListOfChars = 0
        intIndexOfLongestListOfChars = 0

        # loop through all the vectors of matching chars, get the index of the one with the most chars
        for i in range(0, len(listOfListsOfMatchingCharsInSign)):
            if len(listOfListsOfMatchingCharsInSign[i]) > intLenOfLongestListOfChars:
                intLenOfLongestListOfChars = len(listOfListsOfMatchingCharsInSign[i])
                intIndexOfLongestListOfChars = i

        longestListOfMatchingCharsInSign = listOfListsOfMatchingCharsInSign[intIndexOfLongestListOfChars]

        possibleSign.strChar = recognizeCharsInSign(possibleSign.imgThresh, longestListOfMatchingCharsInSign)

        return listOfPossibleSigns


def findPossibleCharsInSign(imgThresh):
    listOfPossibleChars = []
    # imgThreshCopy = imgThresh.copy()

    # find all contours in plate
    imgContours, contours, npaHierarchy = cv2.findContours(imgThresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:  # for each contour
        possibleChar = PossibleChar(contour)

        if checkIfPossibleChar(possibleChar):  # the contour if to a list if it is a possible char
            listOfPossibleChars.append(possibleChar)

    return listOfPossibleChars


def checkIfPossibleChar(possibleChar):
    if (possibleChar.intBoundingRectArea > MIN_PIXEL_AREA and
            possibleChar.intBoundingRectWidth > MIN_PIXEL_WIDTH and
            possibleChar.intBoundingRectHeight > MIN_PIXEL_HEIGHT and
            MIN_ASPECT_RATIO < possibleChar.flatAspectRatio < MAX_ASPECT_RATIO):
        return True
    else:
        return False


def findListOfListsOfMatchingChars(listOfPossibleChars):
    listOfListsOfMatchingChars = []

    for possibleChar in listOfPossibleChars:
        listOfMatchingChars = findListOfMatchingChars(possibleChar, listOfPossibleChars)
        listOfMatchingChars.append(possibleChar)

        if len(listOfMatchingChars) < MIN_NUMBER_OF_MATCHING_CHARS:
            continue

        listOfListsOfMatchingChars.append(listOfMatchingChars)
        listOfPossibleCharsWithCurrentMatchesRemoved = list(set(listOfPossibleChars) - set(listOfMatchingChars))
        recursiveListOfListsOfMatchingChars = findListOfListsOfMatchingChars(
            listOfPossibleCharsWithCurrentMatchesRemoved)

        for recursiveListsOfMatchingChars in recursiveListOfListsOfMatchingChars:
            listOfListsOfMatchingChars.append(recursiveListsOfMatchingChars)

        break

    return listOfListsOfMatchingChars


def findListOfMatchingChars(possibleChar, listOfChars):
    listOfMatchingChars = []

    for possibleMatchingChar in listOfChars:
        if possibleMatchingChar == possibleChar:
            continue
        fltDistanceBetweenChars = distanceBetweenChars(possibleChar, possibleMatchingChar)
        fltAngleBetweenChars = angleBetweenChars(possibleChar, possibleMatchingChar)
        fltChangeInArea = float(
            abs(possibleMatchingChar.intBoundingRectArea - possibleChar.intBoundingRectArea)) / float(
            possibleChar.intBoundingRectArea)

        fltChangeInWidth = float(
            abs(possibleMatchingChar.intBoundingRectWidth - possibleChar.intBoundingRectWidth)) / float(
            possibleChar.intBoundingRectWidth)

        fltChangeInHeight = float(
            abs(possibleMatchingChar.intBoundingRectHeight - possibleChar.intBoundingRectHeight)) / float(
            possibleChar.intBoundingRectHeight)

        if (fltDistanceBetweenChars < (possibleChar.fltDiagonalSize * MAX_DIAG_SIZE_MULTIPLE_AWAY) and
                fltAngleBetweenChars < MAX_ANGLE_BETWEEN_CHARS and
                fltChangeInWidth < MAX_CHANGE_IN_WIDTH and
                fltChangeInArea < MAX_CHANGE_IN_AREA and
                fltChangeInHeight < MAX_CHANGE_IN_HEIGHT):
            listOfMatchingChars.append(possibleMatchingChar)

    return listOfMatchingChars


def distanceBetweenChars(firstChar, secondChar):
    intX = abs(firstChar.intCenterX - secondChar.intCenterX)
    intY = abs(firstChar.intCenterY - secondChar.intCenterY)

    return math.sqrt((intX ** 2) + (intY ** 2))


def angleBetweenChars(firstChar, secondChar):
    fltAdj = float(abs(firstChar.intCenterX - secondChar.intCenterX))
    fltOpp = float(abs(firstChar.intCenterY - secondChar.intCenterY))

    if fltAdj != 0.0:
        fltAngleInRad = math.atan(fltOpp / fltAdj)
    else:
        fltAngleInRad = 1.5708

    fltAngleInDeg = fltAngleInRad * 180.0 / math.pi

    return fltAngleInDeg


def removeInnerOverlappingChars(listOfMatchingChars):
    listOfMatchingCharsWithInnerCharRemoved = list(listOfMatchingChars)

    for currentChar in listOfMatchingChars:
        for otherChar in listOfMatchingChars:
            if currentChar != otherChar:

                if distanceBetweenChars(currentChar, otherChar) < (
                        currentChar.fltDiagonalSize * MIN_DIAG_SIZE_MULTIPLE_AWAY):

                    if currentChar.intBoundingRectArea < otherChar.intBoundingRectArea:
                        if currentChar in listOfMatchingCharsWithInnerCharRemoved:
                            listOfMatchingCharsWithInnerCharRemoved.remove(currentChar)
                    else:
                        if otherChar in listOfMatchingCharsWithInnerCharRemoved:
                            listOfMatchingCharsWithInnerCharRemoved.remove(otherChar)

    return listOfMatchingCharsWithInnerCharRemoved


def recognizeCharsInSign(imgThresh, listOfMatchingChars):
    strChars = ""

    height, width = imgThresh.shape

    imgThreshColor = np.zeros((height, width, 3), np.uint8)
    listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)

    cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2BGR, imgThreshColor)
    # DL = DetectSpeedLimit()
    for currentChar in listOfMatchingChars:
        pt1 = (currentChar.intBoundingRectX, currentChar.intBoundingRectY)
        pt2 = ((currentChar.intBoundingRectX + currentChar.intBoundingRectWidth),
               (currentChar.intBoundingRectY + currentChar.intBoundingRectHeight))

        cv2.rectangle(imgThreshColor, pt1, pt2, (0.0, 255.0, 0.0), 2)

        imgROI = imgThresh[
                 currentChar.intBoundingRectY: currentChar.intBoundingRectY + currentChar.intBoundingRectHeight,
                 currentChar.intBoundingRectX: currentChar.intBoundingRectX + currentChar.intBoundingRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_CHAR_IMAGE_WIDTH, RESIZED_CHAR_IMAGE_HEIGHT))
        npaROIResized = imgROIResized.reshape((1, RESIZED_CHAR_IMAGE_WIDTH * RESIZED_CHAR_IMAGE_HEIGHT))

        npaROIResized = np.float32(npaROIResized)

        retval, npaResults, neigh_resp, dists = KNearest.findNearest(npaROIResized, k=1)
        strCurrentChar = str(chr(int(npaResults[0][0])))

        strChars = strChars + strCurrentChar

    return strChars


def preprocess(imgOriginal):
    imgGray = extractValue(imgOriginal)

    imgGrayMaxContrast = maximizeContrast(imgGray)

    # height, width = imgGray.shape

    # imgBlurred = np.zeros((height, width, 1), np.uint8)
    imgBlurred = cv2.GaussianBlur(imgGrayMaxContrast, GAUSSIAN_SMOOTH_FILTER_SIZE, 0)
    # for i in range(0, len(imgBlurred)):
    #     for j in range(0, len(imgBlurred[0])):
    #         if imgBlurred[i][j] > 50:
    #             imgBlurred[i][j] = 255
    #         else:
    #             imgBlurred[i][j] = 0
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                      ADAPTIVE_THRESH_BLOCK_SIZE, ADAPTIVE_THRESH_WEIGHT)

    return imgGray, imgThresh


def extractValue(imgOriginal):
    height, width, numChannels = imgOriginal.shape
    imgHSV = np.zeros((height, width, 3), np.uint8)
    imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
    imgHue, imgSaturation, imgValue = cv2.split(imgHSV)

    return imgValue


def detectSignsInScene(imgOriginalFrame):
    listOfPossibleSigns = []

    cv2.destroyAllWindows()

    imgGrayFrame, imgThreshFrame = preprocess(imgOriginalFrame)
    listOfPossibleCharsInFrame = findPossibleCharsInFrame(imgThreshFrame)
    listOfListsOfMatchingCharsInFrame = findListOfListsOfMatchingChars(listOfPossibleCharsInFrame)
    for listOfMatchingChars in listOfListsOfMatchingCharsInFrame:
        possibleSign = extractSign(imgOriginalFrame, listOfMatchingChars)

        if possibleSign.imgSign is not None:
            listOfPossibleSigns.append(possibleSign)

    print("\n {0} possible signs found".format(len(listOfPossibleSigns)))

    return listOfPossibleSigns


def findPossibleCharsInFrame(imgThresh):
    listOfPossibleChars = []
    intCountOfPossibleChars = 0
    imgThreshCopy = imgThresh.copy()

    # find all contours
    imgContours, contours, npaHeirarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(0, len(contours)):

        possibleChar = PossibleChar(contours[i])

        if checkIfPossibleChar(possibleChar):
            intCountOfPossibleChars = intCountOfPossibleChars + 1
            listOfPossibleChars.append(possibleChar)

    return listOfPossibleChars


def extractSign(imgOriginal, listOfMatchingChars):
    possibleSign = PossibleSign()

    listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)

    # calculate the center point of the sign
    fltSignCenteX = (listOfMatchingChars[0].intCenterX +
                     listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterX) / 2.0

    fltSignCenterY = (listOfMatchingChars[0].intCenterY +
                      listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterY) / 2.0

    ptSignCenter = fltSignCenteX, fltSignCenterY

    # calculate sign width and height
    intSignWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].intBoundingRectX +
                        listOfMatchingChars[len(listOfMatchingChars) - 1].intBoundingRectWidth -
                        listOfMatchingChars[0].intBoundingRectX) * SIGN_WIDTH_PADDING_FACTOR)

    intTotalOfCharHeights = 0

    for matchingChar in listOfMatchingChars:
        intTotalOfCharHeights += matchingChar.intBoundingRectHeight

    fltAverageCharHeight = intTotalOfCharHeights / len(listOfMatchingChars)

    intSignHeight = int(fltAverageCharHeight * SIGN_HEIGHT_PADDING_FACTOR)

    # calculate the correction angle of sign region
    fltOpposite = listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterY - listOfMatchingChars[0].intCenterY
    fltHypotenuse = distanceBetweenChars(listOfMatchingChars[0],
                                         listOfMatchingChars[len(listOfMatchingChars) - 1])

    fltCorrectionAngleInRad = math.asin(fltOpposite / fltHypotenuse)
    fltCorrectionAngleInDeg = fltCorrectionAngleInRad * 180.0 / math.pi

    # pack sign region center point, width and height, and correction angle into rotated rect member variable of plate
    possibleSign.rrLocationOfSignInFrame = (tuple(ptSignCenter), (intSignWidth, intSignHeight), fltCorrectionAngleInDeg)

    # get the rotation matrix for our calculated correction angle
    rotationMatrix = cv2.getRotationMatrix2D(tuple(ptSignCenter), fltCorrectionAngleInDeg, 1.0)

    height, width, numChannels = imgOriginal.shape
    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (width, height))

    imgCropped = cv2.getRectSubPix(imgRotated, (intSignWidth, intSignHeight), tuple(ptSignCenter))
    possibleSign.imgSign = imgCropped

    return possibleSign
