import datetime
import json
import sys
from time import sleep

from Modules.Classes.Account import Account


def safety_module(acc, time_to_sleep):
    while True:
        try:
            acc.login()
            if acc.chk_get_attacked():
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
            sleep(time_to_sleep)


def get_config(uni):
    with open('Config/Safety_Config.json', encoding="utf-8") as f:
        d = json.load(f)
    return d[uni]


if __name__ == "__main__":
    uni = sys.argv[1]
    config = get_config(uni)
    safety_module(Account(uni, "strabbit@web.de", "OGame!4friends"), config["config"]["waiting_time"])
