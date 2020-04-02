import datetime
import json
import random
import sys
import traceback
from os import path
from time import sleep

import pause

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi

from Classes.Account import Account
from Classes.Coordinate import Coordinate
from Resources.Static_Information.Constants import mission_type_ids


def get_config(uni):
    with open('Config/Expeditions_Config.json', encoding="utf-8") as f:
        d = json.load(f)
    return d[uni]


class Expedition:

    def __init__(self, uni):
        self.config = get_config(uni)
        self.acc = Account(uni, self.config["username"], self.config["password"])
        self.possible_expos = 0
        self.possible_fleets = 0
        self.fleet_gestartet = False

    def thread_expos(self):
        while True:
            try:
                i = 0
                self.fleet_gestartet = False
                self.possible_expos = 1
                self.possible_fleets = 1
                self.acc.login()
                self.acc.init_planets()
                while self.possible_expos > 0 and self.possible_fleets > 0:
                    if not self.chk_for_open_slot():
                        raise AssertionError("No slot available yet, sleeping")
                    self.acc.read_in_all_fleets()
                    planets = self.get_planet_for_expo()
                    self.fleet_gestartet = False
                    while not self.fleet_gestartet:
                        try:
                            self.start_expo(planets[i][0])
                        except ArithmeticError as e:
                            i += 1
                            print("Not enough Deuterium! Trying next: ", planets[i][0].name)
                            pass
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

    def chk_for_open_slot(self):
        self.acc.read_in_mission_count()
        self.acc.read_missions()
        self.possible_expos = (self.acc.expo_count[1] - self.acc.expo_count[0])
        self.possible_fleets = (self.acc.fleet_count[1] - self.acc.fleet_count[0])
        if self.acc.expo_count[1] < 1:
            raise AssertionError("No Expo slots available yet!")

        if self.possible_expos < 1 or self.possible_fleets < 1:
            return_times = []
            for mission in self.acc.missions:
                if mission.return_flight:  # could possibly check for type too if fleet slots were available anyway
                    return_times.append(mission.get_arrival_as_datetime() + datetime.timedelta(0,
                                                                                               15))  # wait 15 seconds after return of fleet to account for delay
            earliest_start = min(dt for dt in return_times)
            print("Pause until", earliest_start)
            pause.until(earliest_start)
            return False
        print("Fleet Slots:", self.possible_fleets, "Expo Slots:", self.possible_expos)
        return True

    def get_planet_for_expo(self):
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
            for ship, attr in self.config["config"]["ships"].items():
                ships.append([planet.ships[ship], attr])
            planet_points.append([planet, sum(ship[1]["point_weight"] * ship[0].count for ship in ships)])

        planet_points_sorted = sorted(planet_points, key=lambda x: (x[1], x[1]), reverse=True)
        return planet_points_sorted

    def start_expo(self, planet):
        min_over_threshold = self.config["config"]["min_over_threshold"]
        ships = []
        ships_send = []
        for ship, attr in self.config["config"]["ships"].items():
            ships.append([planet.ships[ship], attr])

        for ship in ships:
            expo_factor = ship[1]["expo_factor"]
            count_available = ship[0].count
            count_max = ship[1]["max"]
            count_min = ship[1]["min"]
            threshold = min(ship[1]["threshold"], count_available)

            count_calc = int((count_available - threshold) / (expo_factor * self.possible_expos))

            if count_calc >= count_max:
                count_send = count_max
            elif count_calc <= count_min:
                count_send = min(count_min, count_available)
            else:
                count_send = count_calc
            if count_send > 0:
                ships_send.append([ship[0], int(count_send)])

        random_system = random.randint(planet.coordinates.system - self.config["config"]["system_variance"],
                                       planet.coordinates.system + self.config["config"]["system_variance"])

        if ships_send:
            response = planet.send_fleet(mission_type_ids.expedition,
                                         Coordinate(planet.coordinates.galaxy, random_system, 16), ships_send,
                                         resources=[0, 0, 0], speed=10,
                                         holdingtime=1)
        else:  # No ships available for expo
            raise AttributeError

        if not response[0]:
            raise AttributeError

        if response[0]:
            self.possible_expos -= 1
            self.possible_fleets -= 1
            self.fleet_gestartet = True


if __name__ == "__main__":
    uni = sys.argv[1]
    e = Expedition(uni)
    e.thread_expos()
    print("Done...")
