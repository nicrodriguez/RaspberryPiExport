import cv2
import numpy as np

GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
ADAPTIVE_THRESH_BLOCK_SIZE = 25
ADAPTIVE_THRESH_WEIGHT = 12


def preprocess(imgOriginal):
    imgGray = extractValue(imgOriginal)

    imgGrayMaxContrast = maximizeContrast(imgGray)

    height, width = imgGray.shape

    imgBlurred = np.zeros((height, width, 1), np.uint8)
    imgBlurred = cv2.GaussianBlur(imgGrayMaxContrast, GAUSSIAN_SMOOTH_FILTER_SIZE, 0)
    for i in range(0, len(imgBlurred)):
        for j in range(0, len(imgBlurred[0])):
            if imgBlurred[i][j] > 50:
                imgBlurred[i][j] = 255
            else:
                imgBlurred[i][j] = 0
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                      ADAPTIVE_THRESH_BLOCK_SIZE, ADAPTIVE_THRESH_WEIGHT)

    return imgGray, imgThresh


def extractValue(imgOriginal):
    height, width, numChannels = imgOriginal.shape
    imgHSV = np.zeros((height, width, 3), np.uint8)
    imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
    imgHue, imgSaturation, imgValue = cv2.split(imgHSV)

    return imgValue


def maximizeContrast(imgGray):
    height, width = imgGray.shape
    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imgTopHat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, structuringElement)
    imgBlackHat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, structuringElement)

    imgGrayscalePlusTopHat = cv2.add(imgGray, imgTopHat)
    imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

    return imgGrayscalePlusTopHatMinusBlackHat
