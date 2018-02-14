# import the necessary packages
from __future__ import print_function
import threading
from tkinter import *

import datetime

import os

import imutils as imutils
from PIL import Image, ImageTk
import cv2
# from imutils.video import VideoStream
# import argparse
# import time


class FinalGUI:
    def __init__(self, root):
        self.root = root
        self.vs = cv2.VideoCapture(0)
        self.w, self.h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.overrideredirect(1)
        self.root.geometry("%dx%d+0+0" % (self.w, self.h))
        self.root.focus_set()  # <-- move focus to this widget
        self.root.bind("<Escape>", lambda e: e.widget.quit())

        self.videoPanel = Label(self.root)
        self.videoPanel.grid(row=0, rowspan=5, column=0, padx=10, pady=10)

        self.latLabel = Label(self.root, text="Latitude: 89.43242")
        self.latLabel.grid(row=0, column=1, columnspan=2)
        self.latLabel.config(font=("Times New Roman", 40))

        self.lonLabel = Label(self.root, text="Longitude: 24.43242")
        self.lonLabel.grid(row=1, column=1, columnspan=2)
        self.lonLabel.config(font=("Times New Roman", 40))

        self.carSpeedLabel = Label(self.root, text="80")
        self.carSpeedLabel.grid(row=2, column=1)
        self.carSpeedLabel.config(font=("Times New Roman", 80))

        self.carSpeedUnitLabel = Label(self.root, text="mph")
        self.carSpeedUnitLabel.grid(row=2, column=2)
        self.carSpeedUnitLabel.config(font=("Times New Roman", 40))

        self.carSpeedLimitLabel = Label(self.root, text="Limit: 75")
        self.carSpeedLimitLabel.grid(row=3, column=1)
        self.carSpeedLimitLabel.config(font=("Times New Roman", 80))

        self.carSpeedLimitUnitLabel = Label(self.root, text="mph")
        self.carSpeedLimitUnitLabel.grid(row=3, column=2)
        self.carSpeedLimitUnitLabel.config(font=("Times New Roman", 40))
        self.show_frame()

    def show_frame(self):
        _, frame = self.vs.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (int(self.w*7/10), int(self.h*7/10)))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(img)
        self.videoPanel.imgtk = imgtk
        self.videoPanel.configure(image=imgtk)
        self.videoPanel.after(10, self.show_frame)


class PhotoBoothApp:
    def __init__(self, vs, view):

        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None

        self.root = view
        self.panel = None

        btn = Button(self.root, text="Snapshot!", command=self.takeSnapshot)
        btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        self.root.wm_title("PyImageSearch PhotoBooth")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def videoLoop(self):
        # DISCLAIMER:
        # I'm not a GUI developer, nor do I even pretend to be. This
        # try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                _, self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=300)

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image

        except RuntimeError:
            print("[INFO] caught a RuntimeError")

    def takeSnapshot(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))

        # save the file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()


# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-o", "--output", required=True,
#                 help="path to output directory to store snapshots")
# ap.add_argument("-p", "--picamera", type=int, default=-1,
#                 help="whether or not the Raspberry Pi camera should be used")
# args = vars(ap.parse_args())



