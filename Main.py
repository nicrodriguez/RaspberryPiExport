from tkinter import *
from SpeedDetectorGUI import GPSGUI
from DetectSpeedLimit import *
from enum import Enum
from FinalGUI import *


class GUI(Enum):
    MANUAL_GPS = 0
    AUTO_GPS = 1
    FINAL_GUI = 3


showGUI = GUI


gui = showGUI.AUTO_GPS

window = Tk()
if gui == showGUI.MANUAL_GPS:
    GPSGUI(window, 0)
elif gui == showGUI.AUTO_GPS:
    GPSGUI(window, 1)
else:
    FinalGUI(window)

window.mainloop()

# DetectSpeedLimit(0)
