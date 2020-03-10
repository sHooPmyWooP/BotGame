import concurrent.futures
import time

from Classes.Account import Account


def build_next(acc, planet_nr):
    planet = acc.planets[planet_nr]
    metall = planet.buildings["Metallmine"]
    kristall = planet.buildings["Kristallmine"]
    energy = planet.energy
    solar = planet.buildings["Solarkraftwerk"]

    print(planet, metall, kristall, solar, energy)

    if energy < 100:
        if solar.is_possible:
            solar.build()
            solar.level += 1
            time.sleep(solar.construction_time)
            return
        else:
            print(planet.name, "energy_sleep", energy)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return
    print(planet.name, "nach energy check")
    if metall.level - kristall.level > 2:
        if kristall.is_possible:
            kristall.build()
            kristall.level += 1
            time.sleep(kristall.construction_time)
            return
        else:
            print(planet.name, "kristall_sleep", "kristall.is_possible:", kristall.is_possible)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return
    elif (metall.level - kristall.level) <= 2:
        if metall.is_possible:
            metall.build()
            metall.level += 1
            time.sleep(metall.construction_time)
            return
        else:
            print(planet.name, "metall_sleep", "metall.is_possible:", metall.is_possible)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return


def thread_building(planet):
    print("Starting Thread...", planet.name)
    while True:
        # todo: before new check - update buildings & energy
        build_next(a1, planet)
    print(planet.name, "While Loop Broken...")


a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")
print("Login...")

with concurrent.futures.ThreadPoolExecutor() as executor:
    for i, planet in enumerate(a1.planets):
        executor.submit(thread_building, i)
