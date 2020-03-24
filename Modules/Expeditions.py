import datetime
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


class Expedition:

    def __init__(self, acc):
        self.acc = acc
        self.possible_expos = 0
        self.possible_fleets = 0
        self.fleet_gestartet = False

    def start_expo(self, planet):
        ship_sum = 0
        big_t = planet.ships["Großer Transporter"]
        small_t = planet.ships["Kleiner Transporter"]
        pathfinder = planet.ships["Pathfinder"]

        big_t_threshold = min(50, big_t.count)  # safety threshold to keep on planet

        big_t_count = max(min(int((big_t.count - big_t_threshold) / (self.possible_expos * 1)), 250), 0)
        small_t_count = int(small_t.count / self.possible_expos)
        pathfinder_count = int(pathfinder.count / self.possible_expos)

        random_system = random.randint(planet.coordinates.system - 5, planet.coordinates.system + 5)

        ships = [[big_t, big_t_count], [small_t, small_t_count], [pathfinder, pathfinder_count]]
        for i in range(len(ships)):
            ship_sum += ships[i][1]

        if ship_sum > 0:
            response = planet.send_fleet(mission_type_ids.expedition,
                                         Coordinate(planet.coordinates.galaxy, random_system, 16), ships,
                                         resources=[0, 0, 0], speed=10,
                                         holdingtime=1)
        else:  # No ships available for expo
            raise AttributeError

        if not response['success']:
            print(response["errors"])
            if response["errors"][0]["error"] == 4028:  # message = 'Nicht genügend Treibstoff'
                raise ArithmeticError

        if response['success']:
            self.possible_expos -= 1
            self.possible_fleets -= 1
            self.fleet_gestartet = True

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
        planet_t_count = []
        for i in range(len(self.acc.planets)):
            planet = self.acc.planets[i]
            ships = planet.ships
            big_t = ships["Großer Transporter"]
            small_t = ships["Kleiner Transporter"]
            pathfinder = ships["Pathfinder"]
            planet_t_count.append([planet, big_t.count * 12 + small_t.count * 4 + pathfinder.count * 31])
        planet_t_count_sorted = sorted(planet_t_count, key=lambda x: (x[1], x[1]), reverse=True)
        return planet_t_count_sorted

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


e = Expedition(Account("Octans", "strabbit@web.de", "OGame!4friends"))
e.thread_expos()

print("Done...")
