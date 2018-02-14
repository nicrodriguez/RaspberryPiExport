# import the necessary packages
from __future__ import print_function
from tkinter import *
from PIL import Image, ImageTk
import cv2


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
        self.videoPanel.grid(row=0, rowspan=5, column=0, columnspan=3, padx=10, pady=10)

        self.latLabel = Label(self.root, text="Latitude: 89.43242")
        self.latLabel.grid(row=5, column=0, columnspan=1, sticky=N+S+E+W)
        self.latLabel.config(font=("Times New Roman", 40), justify=LEFT, borderwidth=2, relief="groove")

        self.lonLabel = Label(self.root, text="Longitude: 24.43242")
        self.lonLabel.grid(row=5, column=2, columnspan=1, sticky=N+S+E+W)
        self.lonLabel.config(font=("Times New Roman", 40), justify=LEFT, borderwidth=2, relief="groove")

        self.streetLabel = Label(self.root, text="Street Name: Rosemont St")
        self.streetLabel.grid(row=6, column=0, columnspan=3)
        self.streetLabel.config(font=("Times New Roman", 50), justify=CENTER)

        self.carSpeedUnitLabel = Label(self.root, text="Car Speed (mph):")
        self.carSpeedUnitLabel.grid(row=0, column=3)
        self.carSpeedUnitLabel.config(font=("Times New Roman", 40))

        self.carSpeedLabel = Label(self.root, text="80")
        self.carSpeedLabel.grid(row=1, column=3, sticky=N+S+E+W)
        self.carSpeedLabel.config(font=("Times New Roman", 80), borderwidth=2, relief="groove")

        self.carSpeedLimitUnitLabel = Label(self.root, text="Speed Limit (mph):")
        self.carSpeedLimitUnitLabel.grid(row=2, column=3)
        self.carSpeedLimitUnitLabel.config(font=("Times New Roman", 40), justify=LEFT)

        self.carSpeedLimitLabel = Label(self.root, text="75")
        self.carSpeedLimitLabel.grid(row=3, column=3, sticky=N+S+E+W)
        self.carSpeedLimitLabel.config(font=("Times New Roman", 80), justify=RIGHT, borderwidth=2, relief="groove")

        self.detectedLimitPane = Label(self.root)
        self.detectedLimitPane.grid(row=4, column=3, padx=10, pady=10)
        self.show_detected_limit()

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

    def show_detected_limit(self):
        img = cv2.imread("speed_limit_75.png")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        self.detectedLimitPane.img = img
        self.detectedLimitPane.configure(image=img)




