import datetime
import winsound
from time import sleep

from Classes.Account import Account


def sos():
    for i in range(0, 3):
        winsound.Beep(2000, 100)
        for i in range(0, 3):
            winsound.Beep(2000, 400)
            for i in range(0, 3):
                winsound.Beep(2000, 100)


def safety_module(acc, sound=False):
    while True:
        time_to_sleep = 180
        try:
            acc.login()
            if acc.chk_get_attacked():
                if sound:
                    sos()
                acc.read_in_all_planets_basics()
                acc.read_missions()
                target_coords = []
                planets = []
                for mission in acc.missions:
                    if mission.hostile:
                        target_coords.append(mission.coord_to)
                        for coord in target_coords:
                            for planet in acc.planets:
                                if str(planet.coordinates) == str(coord):
                                    planets.append(planet)
                for planet in planets:
                    planet.reader.read_defenses()
                    planet.build_defense_by_ratio()
                    planet.build_defense_routine(1000)
                sleep(time_to_sleep)
            else:
                sleep_until = datetime.datetime.now() + datetime.timedelta(0, time_to_sleep)
                print("Sleep until:", sleep_until)
                sleep(time_to_sleep)
        except Exception as e:
            print("Exception! Sleeping 60 Seconds before retry.", e)
            if sound:
                sos()
            sleep(time_to_sleep)

if __name__ == "__main__":
    safety_module(Account("Octans", "strabbit@web.de", "OGame!4friends"), sound=True)
