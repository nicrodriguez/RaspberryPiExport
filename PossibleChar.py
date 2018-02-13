
import cv2
import math


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

        self.intCenterX = (2*self.intBoundingRectX + self.intBoundingRectWidth) / 2
        self.intCenterY = (2*self.intBoundingRectY + self.intBoundingRectHeight) / 2

        self.fltDiagonalSize = math.sqrt(self.intBoundingRectWidth**2 + self.intBoundingRectHeight**2)

        self.flatAspectRatio = float(self.intBoundingRectWidth) / float(self.intBoundingRectHeight)
