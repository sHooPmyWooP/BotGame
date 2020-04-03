import datetime


class Mission:
    def __init__(self, id, mission_type, return_flight, hostile, coord_from, coord_to, arrival_time):
        self.id = id
        self.mission_type = mission_type
        self.return_flight = return_flight
        self.arrival_time = arrival_time
        self.hostile = hostile
        self.coord_from = coord_from
        self.coord_to = coord_to

    def __repr__(self):
        return "ID: " + str(self.id) + " Type: " + str(self.mission_type) + " from: " + str(
            self.coord_from) + " to: " + str(
            self.coord_to) + " arrival: " + self.get_arrival_as_string() + " hostile: " + str(
            self.hostile) + " return_flight: " + str(self.return_flight)

    def get_arrival_as_datetime(self):
        return datetime.datetime.fromtimestamp(self.arrival_time)

    def get_arrival_as_string(self):
        return self.get_arrival_as_datetime().strftime("%Y-%m-%d %H:%M:%S")
