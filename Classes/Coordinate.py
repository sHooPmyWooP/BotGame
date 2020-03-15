import enum


class Coordinate:
    def __init__(self, galaxy, system, position, destionation):
        self.galaxy = galaxy
        self.system = system
        self.position = position
        self.destination = destionation


class Destination(enum.Enum):
    Planet = 1
    Moon = 2
    Debris = 3
