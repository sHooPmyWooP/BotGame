from math import sqrt
from Classes.Planet import Planet
import random


def send_max_expeditions(acc):
    expoResearch = acc.research['Astrophysik']
    maxExpos = int(sqrt(expoResearch.level)) + 1
    for expo in range(0, maxExpos):
        planet = Planet(random.choice(acc.planets))
        shipsOnPlanet = planet.get_ships(planet.id)
        # TODO: sendFleetFromPlanet