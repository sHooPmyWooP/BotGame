import enum
import math


class Coordinate:
    def __init__(self, galaxy=0, system=0, position=0, destination=1):
        self.galaxy = int(galaxy)
        self.system = int(system)
        self.position = int(position)
        self.destination = destination

    def get_coord_str(self):
        return f"{self.galaxy}:{self.system}:{self.position}"

    @staticmethod
    def create_from_string(s):
        s = s.split(':')
        return Coordinate(s[0], s[1], s[2])

    @staticmethod
    def get_distance(c1, c2):
        # TODO: Add donut Galaxy calculation
        if c1.galaxy != c2.galaxy:
            return int(math.fabs(c1.galaxy - c2.galaxy) * 20000)
        elif c1.system != c2.system:
            return int(math.fabs(c1.system - c2.system) * 95 + 2700)
        else:
            return int(math.fabs(c1.position - c2.position) * 5 + 1000)

    def __repr__(self):
        return f"{self.galaxy}:{self.system}:{self.position}-{self.destination}"

    def get_own_celestials_in_range(self, celestials, radius):
        """
        Get a list of celestials in range of a certain coordinate
        :param celestials: Celestial[ ]
        :param radius: int
        :return: Celestial[ ]
        """
        celestials_in_range = []
        min_system = min(self.system - radius, 1)
        max_system = max(self.system + radius, 499)
        for celestial in celestials:
            if celestial.coordinates.galaxy == self.galaxy:
                if min_system <= celestial.coordinates.system <= max_system:
                    celestials_in_range.append(celestial)
        return celestials_in_range

    def calculate_relative_distance(self, other):
        galaxy_dis = abs(self.galaxy - other.galaxy)
        system_dis = abs(self.system - other.system)
        position_dis = abs(self.position - other.position)

        return galaxy_dis * 100 + system_dis * 10 + position_dis

class Destination(enum.Enum):
    Planet = 1
    Moon = 2
    Debris = 3
