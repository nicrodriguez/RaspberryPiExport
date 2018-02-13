import cv2
import math

import ImageProcessing
import DetectChars
import PossibleSign
import PossibleChar

SIGN_WIDTH_PADDING_FACTOR = 1.3
SIGN_HEIGHT_PADDING_FACTOR = 1.5


def detectSignsInScene(imgOriginalFrame):
    listOfPossibleSigns = []

    cv2.destroyAllWindows()

    imgGrayFrame, imgThreshFrame = ImageProcessing.preprocess(imgOriginalFrame)
    listOfPossibleCharsInFrame = findPossibleCharsInFrame(imgThreshFrame)
    listOfListsOfMatchingCharsInFrame = DetectChars.findListOfListsOfMatchingChars(listOfPossibleCharsInFrame)
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

        possibleChar = PossibleChar.PossibleChar(contours[i])

        if DetectChars.checkIfPossibleChar(possibleChar):
            intCountOfPossibleChars = intCountOfPossibleChars+1
            listOfPossibleChars.append(possibleChar)

    return listOfPossibleChars


def extractSign(imgOriginal, listOfMatchingChars):
    possibleSign = PossibleSign.PossibleSign()

    listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)

    # calculate the center point of the sign
    fltSignCenteX = (listOfMatchingChars[0].intCenterX +
                     listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterX)/2.0

    fltSignCenterY = (listOfMatchingChars[0].intCenterY +
                      listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterY)/2.0

    ptSignCenter = fltSignCenteX, fltSignCenterY

    # calculate sign width and height
    intSignWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].intBoundingRectX +
                        listOfMatchingChars[len(listOfMatchingChars) - 1].intBoundingRectWidth -
                        listOfMatchingChars[0].intBoundingRectX) * SIGN_WIDTH_PADDING_FACTOR)

    intTotalOfCharHeights = 0

    for matchingChar in listOfMatchingChars:
        intTotalOfCharHeights += matchingChar.intBoundingRectHeight

    fltAverageCharHeight = intTotalOfCharHeights/len(listOfMatchingChars)

    intSignHeight = int(fltAverageCharHeight * SIGN_HEIGHT_PADDING_FACTOR)

    # calculate the correction angle of sign region
    fltOpposite = listOfMatchingChars[len(listOfMatchingChars) - 1].intCenterY - listOfMatchingChars[0].intCenterY
    fltHypotenuse = DetectChars.distanceBetweenChars(listOfMatchingChars[0],
                                                     listOfMatchingChars[len(listOfMatchingChars) - 1])

    fltCorrectionAngleInRad = math.asin(fltOpposite/fltHypotenuse)
    fltCorrectionAngleInDeg = fltCorrectionAngleInRad * 180.0/math.pi

    # pack sign region center point, width and height, and correction angle into rotated rect member variable of plate
    possibleSign.rrLocationOfSignInFrame = (tuple(ptSignCenter), (intSignWidth, intSignHeight), fltCorrectionAngleInDeg)

    # get the rotation matrix for our calculated correction angle
    rotationMatrix = cv2.getRotationMatrix2D(tuple(ptSignCenter), fltCorrectionAngleInDeg, 1.0)

    height, width, numChannels = imgOriginal.shape
    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (width, height))

    imgCropped = cv2.getRectSubPix(imgRotated, (intSignWidth, intSignHeight), tuple(ptSignCenter))
    possibleSign.imgSign = imgCropped

    return possibleSign
