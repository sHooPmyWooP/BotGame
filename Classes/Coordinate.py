import enum


class Coordinate:
    def __init__(self, galaxy, system, position, destination=1):
        self.galaxy = galaxy
        self.system = system
        self.position = position
        self.destination = destination


class Destination(enum.Enum):
    Planet = 1
    Moon = 2
    Debris = 3
