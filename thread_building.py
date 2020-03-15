import time
from concurrent.futures import ThreadPoolExecutor

from Classes.Account import Account


def build_next(acc, planet):
    metall = planet.buildings["Metallmine"]
    kristall = planet.buildings["Kristallmine"]
    energy = planet.energy
    solar = planet.buildings["Solarkraftwerk"]

    print(planet, metall, kristall, solar, energy)

    for building in planet.buildings:
        # print(planet.buildings[building].id)
        if planet.buildings[building].in_construction:
            print(
                f"sleeping due to construction of {building} for {planet.buildings[building].construction_finished_in_seconds}s")
            time.sleep(planet.buildings[building].construction_finished_in_seconds)
            return

    if metall.level - kristall.level > 2:
        if int(kristall.energy_consumption_nxt_level) >= int(energy):
            if solar.is_possible:
                solar.build()
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "kristall_energy_sleep", "energy.is_possible:", energy.is_possible)
                time.sleep(60)  # todo: calculate time until production is possible and run again
                return
        if kristall.is_possible:
            kristall.build()
            time.sleep(kristall.construction_time)
            return
        else:
            print(planet.name, "kristall_sleep", "kristall.is_possible:", kristall.is_possible)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return
    if (metall.level - kristall.level) <= 2:
        if metall.energy_consumption_nxt_level >= energy:
            if solar.is_possible:
                solar.build()
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "metall_energy_sleep", "energy.is_possible:", energy.is_possible)
                time.sleep(60)  # todo: calculate time until production is possible and run again
                return
        if metall.is_possible:
            metall.build()
            time.sleep(metall.construction_time)
            return
        else:
            print(planet.name, "metall_sleep", "metall.is_possible:", metall.is_possible)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return


def thread_building(planet):
    print("Starting Thread...")
    while True:
        # todo: before new check - update buildings & energy
        a1.read_in_planet(planet.id)
        build_next(a1, planet)


a1 = Account("Octans", "david-achilles@hotmail.de", "OGame!4friends")
a1.read_in_all_planets()

# thread_building(2)
with ThreadPoolExecutor() as executor:
    for i in range(len(a1.planets)):
        executor.submit(thread_building, a1.planets[i])

print("Done...")
