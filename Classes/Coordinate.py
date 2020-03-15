import enum


class Coordinate:
    def __init__(self, galaxy=0, system=0, position=0, destination=1):
        self.galaxy = galaxy
        self.system = system
        self.position = position
        self.destination = destination

    def get_coord_str(self):
        return f"{self.galaxy}:{self.system}:{self.position}"

class Destination(enum.Enum):
    Planet = 1
    Moon = 2
    Debris = 3
