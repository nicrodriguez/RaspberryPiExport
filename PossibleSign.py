import cv2
import numpy as np


class PossibleSign:

    def __init__(self):
        self.imgSign = None
        self.imgGray = None
        self.imgThresh = None

        self.rrLocationOfSignInFrame = None

        self.strChar = ""
