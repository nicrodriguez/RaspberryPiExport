from tkinter import *
from DatabaseHelper import *

import time


class GPSGUI(object):
    db = DatabaseHelper("SpeedLimits.db")

    def __init__(self, view, guiType):
        self.view = view
        if guiType == 0:

            lat_text = StringVar()
            self.lat_entry = Entry(self.view, textvariable=lat_text)

            lon_text = StringVar()
            self.lon_entry = Entry(self.view, textvariable=lon_text)

            self.street_label = Label(self.view, text="--", width=25)
            self.speed_limit_label = Label(self.view, text="-- mph")
            self.search_time = Label(self.view, text="Search Time:")
            self.search_time_label = Label(self.view, text="-- seconds")

            self.manualGUI(self.view)

        elif guiType == 1:
            self.lat_label = Label(self.view, text="Latitude: --")
            self.lon_label = Label(self.view, text="Longitude: --")
            self.speed_label_num = Label(self.view, text="80")
            self.speed_label_unit = Label(self.view, text="mph")
            self.speed_limit_label = Label(self.view, text="Speed Limit: --")
            self.autoGUI(view)
        else:
            print("invalid GUI specification")
            return

    def manualGUI(self, view):

        lat_label = Label(view, text="Lat: ")
        lat_label.grid(row=0, column=0)

        lat_text = StringVar()
        self.lat_entry = Entry(view, textvariable=lat_text)
        self.lat_entry.grid(row=0, column=1, columnspan=2)

        lon_label = Label(view, text="Lon: ")
        lon_label.grid(row=0, column=3)

        self.lon_entry.grid(row=0, column=4, columnspan=2)

        enter_button = Button(view, text="Query", command=self.get_limit)
        enter_button.grid(row=0, column=6)

        road_label = Label(view, text="Road: ")
        road_label.grid(row=1, column=0, columnspan=2)
        road_label.config(font=("Times New Roman", 40))

        self.street_label.grid(row=1, column=2, columnspan=5)
        self.street_label.config(font=("Times New Roman", 40))

        self.speed_limit_label.grid(row=2, column=2, rowspan=2, columnspan=4)
        self.speed_limit_label.config(font=("Times New Roman", 80))

        self.search_time.grid(row=4, column=4)
        self.search_time_label.grid(row=4, column=5)

    def autoGUI(self, view):
        self.lat_label.grid(row=0, column=0, columnspan=2)
        self.lon_label.grid(row=0, column=2, columnspan=2)

        self.speed_label_num.grid(row=1, column=0, columnspan=3)
        self.speed_label_num.config(font=("Times New Roman", 80))

        self.speed_label_unit.grid(row=1, column=3, columnspan=1)
        self.speed_label_unit.config(font=("Times New Roman", 20))

        self.speed_limit_label.grid(row=2, column=0, columnspan=4)
        self.speed_limit_label.config(font=("Times New Roman", 40))
        print("AutoGUI")

    def get_limit(self):
        start = time.clock()
        vals = self.db.get_speed_limit(float(self.lat_entry.get()), float(self.lon_entry.get()))
        end = time.clock()
        self.search_time_label.config(text='{0:.5f} seconds'.format(end - start))

        if type(vals) != str:
            print('{0}, {1}'.format(vals[0], vals[1]))
            self.street_label.config(text='{0}'.format(vals[0]))
            self.speed_limit_label.config(text='{0} mph'.format(vals[1]))
            self.set_speed(vals[1])
        else:
            self.street_label.config(text='{0}'.format(vals))
            self.speed_limit_label.config(text='-- mph')
            print(vals)
        print("ManualGUI")


    @staticmethod
    def set_speed(speed):
        new_line = 'Max Speed:{0}'.format(speed) + '\n'
        config_temp = 'Para.cfg'
        with open(config_temp, 'r+') as f:
            content = f.readlines()
            f.seek(0)
            for line in content:
                if 'Max Speed' in line:
                    line = line.replace(line, new_line)
                f.write(line)
            f.truncate()
