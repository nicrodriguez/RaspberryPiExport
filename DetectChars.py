import cv2
import numpy as np
import math

from DetectSpeedLimit import *
import ImageProcessing
import PossibleChar
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


# Loading in training classifications and training data
def loadKNNDataAndTrainKNN():
    try:
        npaClassifications = np.loadtxt("classifications1.txt", np.float32)
    except:
        print("Error, unable to open classifications.txt, exiting program\n")
        return False

    try:
        npaFlattenedImages = np.loadtxt("flattened_images1.txt", np.float32)
    except:
        print("Error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return False

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    KNearest.setDefaultK(1)
    KNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    return True


def detectCharsInSign(listOfPossibleSigns):

    if len(listOfPossibleSigns) == 0:
        return listOfPossibleSigns

    for possibleSign in listOfPossibleSigns:
        possibleSign.imgGray, possibleSign.imgThresh = ImageProcessing.preprocess(possibleSign.imgSign)

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
    imgThreshCopy = imgThresh.copy()

    # find all contours in plate
    imgContours, contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:  # for each contour
        possibleChar = PossibleChar.PossibleChar(contour)

        if checkIfPossibleChar(possibleChar):   # the contour if to a list if it is a possible char
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
            abs(possibleMatchingChar.intBoundingRectArea - possibleChar.intBoundingRectArea))/float(
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
        fltAngleInRad = math.atan(fltOpp/fltAdj)
    else:
        fltAngleInRad = 1.5708

    fltAngleInDeg = fltAngleInRad*180.0/math.pi

    return fltAngleInDeg


def removeInnerOverlappingChars(listOfMatchingChars):
    listOfMatchingCharsWithInnerCharRemoved = list(listOfMatchingChars)

    for currentChar in listOfMatchingChars:
        for otherChar in listOfMatchingChars:
            if currentChar != otherChar:

                if distanceBetweenChars(currentChar, otherChar) < (
                        currentChar.fltDiagonalSize*MIN_DIAG_SIZE_MULTIPLE_AWAY):

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
        npaROIResized = imgROIResized.reshape((1, RESIZED_CHAR_IMAGE_WIDTH*RESIZED_CHAR_IMAGE_HEIGHT))

        npaROIResized = np.float32(npaROIResized)

        retval, npaResults, neigh_resp, dists = KNearest.findNearest(npaROIResized, k=1)
        strCurrentChar = str(chr(int(npaResults[0][0])))

        strChars = strChars+strCurrentChar

    return strChars
