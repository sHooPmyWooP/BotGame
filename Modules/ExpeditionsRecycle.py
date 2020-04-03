import datetime
import json
import sys
import traceback
from os import path
from time import sleep

import pause

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi

from Modules.Classes import Account
from Modules.Classes import Coordinate
from Modules.Resources.Static_Information.Constants import mission_type_ids


def get_config(uni):
    with open('Config/Expeditions_Config.json', encoding="utf-8") as f:
        d = json.load(f)
    return d[uni]


class ExpeditionRecycle:

    def __init__(self, uni):
        self.config = get_config(uni)
        self.acc = Account(uni, self.config["username"], self.config["password"])
        self.possible_fleets = 0
        self.fleet_gestartet = False

    def chk_for_open_slot(self):
        self.acc.read_in_mission_count()
        self.acc.read_missions()
        self.possible_fleets = (self.acc.fleet_count[1] - self.acc.fleet_count[0])

        if self.possible_fleets < 1:
            return_times = []
            for mission in self.acc.missions:
                if mission.return_flight:  # could possibly check for type too if fleet slots were available anyway
                    return_times.append(mission.get_arrival_as_datetime() + datetime.timedelta(0,
                                                                                               15))  # wait 15 seconds after return of fleet to account for delay
            earliest_start = min(dt for dt in return_times)
            print("Pause until", earliest_start)
            pause.until(earliest_start)
            return False
        print("Fleet Slots:", self.possible_fleets)
        return True

    def get_planet_for_recycling(self):
        for planet in self.acc.planets:
            print("--------", planet.name, "--------")
            for ship in planet.ships:
                if planet.ships[ship].count:
                    print("{:.<22}".format(planet.ships[ship].name) + " -> amount: " + '{: >10}'.format(
                        planet.ships[ship].count))

        planet_points = []
        for i in range(len(self.acc.planets)):
            planet = self.acc.planets[i]
            ships = []
            planet_points.append([planet, planet.ships["Pathfinder"].count])

        planet_points_sorted = sorted(planet_points, key=lambda x: (x[1], x[1]), reverse=True)
        return planet_points_sorted

    def start_recycling(self, planet):
        ships = []

        pathfinder = planet.ships["Pathfinder"]
        count_available = pathfinder.count
        count_max = 50
        threshold = 50

        if count_available > count_max:
            count_send = count_max
        elif count_available <= 0:
            count_send = 0
        else:
            count_send = count_available

        ships_send = []
        ships_send.append([pathfinder, int(count_send)])

        if count_send:
            response = planet.send_fleet(mission_type_ids.recycle,
                                         Coordinate(planet.coordinates.galaxy, planet.coordinates.system, 16),
                                         ships_send,
                                         resources=[0, 0, 0], speed=10,
                                         holdingtime=0)
        else:  # No ships available for expo
            raise AttributeError

        if not response[0]:
            raise AttributeError

        if response[0]:
            self.possible_fleets -= 1
            self.fleet_gestartet = True
            sleep(60 * 30)  # 30 min

    def run_recycling(self):
        while True:
            try:
                i = 0
                self.fleet_gestartet = False
                self.possible_fleets = 1
                self.acc.login()
                self.acc.init_planets()
                while self.possible_fleets > 0:
                    if not self.chk_for_open_slot():
                        raise AssertionError("No slot available yet, sleeping")
                    self.acc.read_in_all_fleets()
                    planets = self.get_planet_for_recycling()
                    self.fleet_gestartet = False
                    while not self.fleet_gestartet:
                        try:
                            self.start_recycling(planets[i][0])
                        except AttributeError as e:
                            print("No Ships available, sleeping 60 seconds")
                            sleep(60)
                            pass
            except ConnectionError as e:
                print("Connection failed...", e)
                sleep(60)
            except AssertionError:
                traceback.print_exc()
                pass
            except Exception as e:
                traceback.print_exc()
                pass


if __name__ == "__main__":
    uni = sys.argv[1]
    e = ExpeditionRecycle(uni)
    e.run_recycling()
    print("Done...")
