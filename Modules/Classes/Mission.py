import datetime

try:  # Resources
    from .Resources import Resources
except ModuleNotFoundError:
    from Modules.Classes.Resources import Resources
except ImportError:
    from Modules.Classes.Resources import Resources


class Mission:
    def __init__(self, id, mission_type, return_flight, hostile, coord_from, coord_to, arrival_time,
                 resources=Resources(), ships=None):
        """
        :param id: int
        :param mission_type: mission_type_id
        :param return_flight: Boolean
        :param hostile: Boolean
        :param coord_from: Coordinate
        :param coord_to: Coordinate
        :param arrival_time:
        :param resources: Ressources
        :param ships: [[Name, Quantity],]
        """
        if ships is None:
            ships = [[]]
        self.id = id
        self.mission_type = mission_type
        self.return_flight = return_flight
        self.arrival_time = arrival_time
        self.hostile = hostile
        self.coord_from = coord_from
        self.coord_to = coord_to
        self.resources = resources
        self.ships = ships

    def __repr__(self):
        return "ID: " + str(self.id) + " Type: " + str(self.mission_type) + " from: " + str(
            self.coord_from) + " to: " + str(
            self.coord_to) + " arrival: " + self.get_arrival_as_string() + " hostile: " + str(
            self.hostile) + " return_flight: " + str(self.return_flight)

    def get_arrival_as_datetime(self):
        return datetime.datetime.fromtimestamp(self.arrival_time)

    def get_arrival_as_string(self):
        return self.get_arrival_as_datetime().strftime("%Y-%m-%d %H:%M:%S")
