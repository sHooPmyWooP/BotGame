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

    for building in planet.buildings:
        # print(planet.buildings[building].id)
        if planet.buildings[building].in_construction:
            print(f"sleeping due to construction of {building}")
            time.sleep(60)
            return

    if metall.level - kristall.level > 2:
        print(kristall.energy_consumption)
        if int(kristall.energy_consumption) >= int(energy):
            if solar.is_possible:
                solar.build()
                solar.level += 1
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "kristall_energy_sleep", "energy.is_possible:", energy.is_possible)
                time.sleep(60)  # todo: calculate time until production is possible and run again
                return
        if kristall.is_possible:
            kristall.build()
            kristall.level += 1
            time.sleep(kristall.construction_time)
            return
        else:
            print(planet.name, "kristall_sleep", "kristall.is_possible:", kristall.is_possible)
            time.sleep(60)  # todo: calculate time until production is possible and run again
            return
    print(metall.energy_consumption)
    if (metall.level - kristall.level) <= 2:
        if metall.energy_consumption >= energy:
            if solar.is_possible:
                solar.build()
                solar.level += 1
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "metall_energy_sleep", "energy.is_possible:", energy.is_possible)
                time.sleep(60)  # todo: calculate time until production is possible and run again
                return
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
    print("Starting Thread...")
    while True:
        # todo: before new check - update buildings & energy - vorübergehend mit neuem login gelöst
        build_next(a1, planet)
        a1.login()


a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")

with concurrent.futures.ThreadPoolExecutor() as executor:
    p0 = executor.submit(thread_building, 0)
    p1 = executor.submit(thread_building, 1)
    # for i, planet in enumerate(a1.planets):
    #     print(i)
    #     executor.submit(thread_building, i)
