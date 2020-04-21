import enum


class Coordinate:
    def __init__(self, galaxy=0, system=0, position=0, destination=1):
        self.galaxy = int(galaxy)
        self.system = int(system)
        self.position = int(position)
        self.destination = destination

    def get_coord_str(self):
        return f"{self.galaxy}:{self.system}:{self.position}"

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
            if celestial.galaxy == self.galaxy:
                if min_system <= celestial.system <= max_system:
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
