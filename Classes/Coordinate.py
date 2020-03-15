import enum


class Coordinate:
    def __init__(self):
        self.galaxy = 0
        self.system = 0
        self.position = 0
        self.destination = Destination


class Destination(enum.Enum):
    Planet = 1
    Moon = 2
    Debris = 3
