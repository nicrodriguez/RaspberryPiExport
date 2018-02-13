import sqlite3


class DatabaseHelper:
    def __init__(self, database):
        self.gps_data = ''
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()

        print("Database Connection Initiated")
        self.cur.execute("SELECT road FROM SpeedLimits")
        self.road_list = self.cur.fetchall()

        self.cur.execute("SELECT lat FROM SpeedLimits")
        self.lat_list = self.cur.fetchall()

        self.cur.execute("SELECT lon FROM SpeedLimits")
        self.lon_list = self.cur.fetchall()

        self.cur.execute("SELECT speed_limit FROM SpeedLimits")
        self.speed_list = self.cur.fetchall()

    def get_speed_limit(self, lat, lon):

        vals = []
        for k in range(len(self.lat_list)):
            if float(self.lat_list[k][0]) - 0.00008 <= lat < float(self.lat_list[k][0]) + 0.00008:
                if float(self.lon_list[k][0]) - 0.00005 <= lon < float(self.lon_list[k][0]) + 0.00005:
                    vals.append(k)
                    return [self.road_list[k][0], self.speed_list[k][0]]

        if len(vals) == 0:
            for k in range(len(self.lat_list)):
                if float(self.lon_list[k][0]) - 0.00009 <= lon < float(self.lon_list[k][0]) + 0.00009:
                    if float(self.lat_list[k][0]) - 0.00005 <= lat < float(self.lat_list[k][0]) + 0.00005:
                        return [self.road_list[k][0], self.speed_list[k][0]]

        if len(vals) == 0:
            return 'UNCHARTED TERRITORY'

        return vals

    def parse_data(self, gps_data):
        self.gps_data = gps_data.split(',')
        lat = self.gps_data[2]
        lon = self.gps_data[3]

        return lat, lon

    def __del__(self):
        self.con.close()
        print("Database Connection Closed")