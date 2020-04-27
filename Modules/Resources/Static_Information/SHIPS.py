from enum import Enum
from Modules.Classes.Resources import Resources


class Ships(Enum):
    # Battleships
    LIGHT_FIGHTER = 204
    HEAVY_FIGHTER = 205
    CRUISER = 206
    BATTLESHIP = 207
    BATTLECRUISER = 215
    BOMBER = 211
    DESTROYER = 213
    DEATHSTAR = 214
    REAPER = 218
    PATHFINDER = 219

    # Civil ships
    SMALL_TRANSPORTER = 202
    LARGE_TRANSPORTER = 203
    COLONY_SHIP = 208
    RECYCLER = 209
    ESPIONAGE_PROBE = 210
    SOLAR_SATELLITE = 212
    CRAWLER = 217

    def id(self):
        return self.value

    def costs(self):
        costs = datas[self.id()]
        return Resources(costs['costs_metal'], costs['costs_crystal'], costs['costs_deut'])

    def cargo(self):
        return datas[self.id()]['base_cargo']

    def fuel_consumption(self):
        return datas[self.id()]['fuel_consumption']

    def __str__(self):
        return datas[self.id()]['name']


datas = {
    204: {
        "name": "Leichter Jäger",
        "costs_metal": 3000,
        "costs_crystal": 1000,
        "costs_deut": 0,
        "base_cargo": 50,
        "fuel_consumption": 20,
    }   # TODO: Add missing Ship Infos
}

print(Ships.LIGHT_FIGHTER.costs())
print(Ships.LIGHT_FIGHTER)
print(Ships.LIGHT_FIGHTER.cargo())
print(Ships(204).costs())
