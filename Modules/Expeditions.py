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

from Modules.Classes.Account import Account
from Modules.Classes.Coordinate import Coordinate

try:
    from Modules.Resources.Static_Information.Constants import mission_type_ids
except ModuleNotFoundError:
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
        self.fleet_started = False
        self.max_wait_time = self.config["config"]["max_wait_time"]
        self.time_between_expos = self.config["config"]["time_between_expos"]

    def thread_expos(self):
        while True:
            try:
                i = 0
                self.fleet_started = False
                self.possible_expos = 1
                self.possible_fleets = 1
                self.acc.login()
                self.acc.init_celestials()
                while self.possible_expos > 0 and self.possible_fleets > 0:
                    if not self.chk_for_open_slot():
                        raise AssertionError("No slot available yet, sleeping")
                    self.acc.read_in_all_fleets()
                    celestials = self.get_celestial_for_expo(self.config["config"]["fly_from_moon"])
                    self.fleet_started = False
                    while not self.fleet_started:
                        try:
                            self.start_expo(celestials[i][0])
                        except ArithmeticError as e:
                            i += 1
                            print("Not enough Deuterium! Trying next: ", celestials[i][0].name)
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
            if self.possible_fleets < 1:
                relevant_missions = [mission for mission in self.acc.missions
                                     if mission.return_flight]
            else:
                relevant_missions = [mission for mission in self.acc.missions
                                     if mission.mission_type == mission_type_ids.expedition
                                     and mission.return_flight]
            for mission in relevant_missions:
                return_times.append(mission.get_arrival_as_datetime() + datetime.timedelta(0, self.time_between_expos))
            earliest_start = min(dt for dt in return_times)
            earliest_start = min(earliest_start, datetime.datetime.now() + datetime.timedelta(0, self.max_wait_time))
            print("Pause until", earliest_start)
            pause.until(earliest_start)
            return False
        print("Fleet Slots:", self.possible_fleets, "Expo Slots:", self.possible_expos)
        return True

    def get_celestial_for_expo(self, from_moon):
        celestials = self.acc.planets if not from_moon else self.acc.moons
        for celestial in celestials:
            print("--------", celestial.name, "--------")
            for ship in celestial.ships:
                if celestial.ships[ship].count:
                    print("{:.<22}".format(celestial.ships[ship].name) + " -> amount: " + '{: >10}'.format(
                        celestial.ships[ship].count))

        celestial_points = []
        for i in range(len(celestials)):
            celestial = celestials[i]
            ships = []
            for ship, attr in self.config["config"]["ships"].items():
                ships.append([celestial.ships[ship], attr])
            celestial_points.append([celestial, sum(ship[1]["point_weight"] * ship[0].count for ship in ships)])

        celestial_points_sorted = sorted(celestial_points, key=lambda x: (x[1], x[1]), reverse=True)
        return celestial_points_sorted

    def start_expo(self, celestial):
        min_over_threshold = self.config["config"]["min_over_threshold"]
        ships = []
        ships_send = []
        for ship, attr in self.config["config"]["ships"].items():
            ships.append([celestial.ships[ship], attr])

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

        random_system = random.randint(celestial.coordinates.system - self.config["config"]["system_variance"],
                                       celestial.coordinates.system + self.config["config"]["system_variance"])

        if ships_send:
            response = celestial.send_fleet(mission_type_ids.expedition,
                                            Coordinate(celestial.coordinates.galaxy, random_system, 16), ships_send,
                                            resources=[0, 0, 0], speed=10,
                                            holdingtime=1)
        else:  # No ships available for expo
            raise AttributeError

        if not response[0]:
            raise AttributeError

        if response[0]:
            self.possible_expos -= 1
            self.possible_fleets -= 1
            self.fleet_started = True


if __name__ == "__main__":
    universe = sys.argv[1]
    e = Expedition(universe)
    e.thread_expos()
    print("Done...")
