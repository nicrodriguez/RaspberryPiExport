from tkinter import Tk
from FinalGUI import FinalGUI
from SpeedDetectorGUI import GPSGUI


def main():
    window = Tk()
    FinalGUI(window)
    # GPSGUI(window, 0)
    window.mainloop()


if __name__ == '__main__':
    main()
