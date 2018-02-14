from enum import Enum
from DetectSpeedLimit import *
from FinalGUI import *
from SpeedDetectorGUI import GPSGUI


class Action(Enum):
    MANUAL_GPS = 0
    AUTO_GPS = 1
    IMG_PROC = 2
    FINAL_GUI = 3


displayGUI = True  # Determine if you want to run the GUIs or not
if displayGUI:
    showGUI = Action

    gui = showGUI.FINAL_GUI  # Pick which GUI you want to run
    window = Tk()
    if gui == showGUI.MANUAL_GPS:
        GPSGUI(window, 0)
    elif gui == showGUI.AUTO_GPS:
        GPSGUI(window, 1)
    else:
        FinalGUI(window)
    window.mainloop()

else:
    DetectSpeedLimit(0)






