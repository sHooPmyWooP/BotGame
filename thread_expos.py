import datetime
import random
from time import sleep

import pause

from Classes.Account import Account
from Classes.Coordinate import Coordinate
from Resources.Static_Information.Constants import mission_type_ids


class Expedition:

    def __init__(self, acc):
        self.acc = acc
        self.possible_expos = 0
        self.possible_fleets = 0

    def start_expo(self, planet):
        big_t = planet.ships["Großer Transporter"]
        small_t = planet.ships["Kleiner Transporter"]
        pathfinder = planet.ships["Pathfinder"]

        big_t_threshold = min(50, big_t.count)  # safety threshold to keep on planet

        big_t_count = max(min(int((big_t.count - big_t_threshold) / (self.possible_expos * 1.5)), 250), 0)
        small_t_count = int(small_t.count / self.possible_expos)
        pathfinder_count = int(pathfinder.count / self.possible_expos)

        random_system = random.randint(planet.coordinates.system - 5, planet.coordinates.system + 5)

        ships = [[big_t, big_t_count], [small_t, small_t_count], [pathfinder, pathfinder_count]]
        response = planet.send_fleet(mission_type_ids.expedition,
                                     Coordinate(planet.coordinates.galaxy, random_system, 16), ships,
                                     resources=[0, 0, 0], speed=10,
                                     holdingtime=1)

        if not response['success']:
            print(response["errors"])
            return

        if response['success']:
            print("Mission started")
            self.possible_expos -= 1
            self.possible_fleets -= 1

    def chk_for_open_slot(self):
        self.acc.check_fleet_slots()
        self.possible_expos = (self.acc.expo_count[1] - self.acc.expo_count[0])
        self.possible_fleets = (self.acc.fleet_count[1] - self.acc.fleet_count[0])
        if self.acc.expo_count[1] < 1:
            raise AssertionError("No Expo slots available yet!")

        if self.possible_expos < 1 or self.possible_fleets < 1:
            return_times = []
            for mission in self.acc.missions:
                if self.acc.missions[mission][
                    "return_flight"]:  # could possibly check for type too if fleet slots were available anyway
                    return_times.append(self.acc.missions[mission]["timestamp_arrival"] + datetime.timedelta(0,
                                                                                                             15))  #
                    # wait 15 seconds after return of fleet to account for delay
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
        return planet_t_count_sorted[0][0]

    def thread_expos(self):
        print("Starting Thread...")
        while True:
            try:
                self.possible_expos = 1
                self.possible_fleets = 1
                self.acc.login()
                self.acc.read_in_all_planets()
                while self.possible_expos > 0 and self.possible_fleets > 0:
                    if not self.chk_for_open_slot():
                        raise AssertionError("No slot available yet, sleeping")
                    self.acc.read_in_all_fleets()
                    planet = self.get_planet_for_expo()
                    self.start_expo(planet)
            except ConnectionError as e:
                print("Connection failed...", e)
                sleep(60)
            except AssertionError:
                print("AssError")
                pass
            except Exception as e:
                print(e)
                pass


a1 = Account("Octans", "david-achilles@hotmail.de", "OGame!4friends")
e = Expedition(a1)
e.thread_expos()

# thread_expos(a1.planets[0])
# with ThreadPoolExecutor() as executor:
#     expo1 = executor.submit(thread_expos, a1.planets[0])

print("Done...")
