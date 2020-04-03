import datetime
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from Modules.Classes import Account


def build_next(planet):
    metall = planet.buildings["Metallmine"]
    kristall = planet.buildings["Kristallmine"]
    energy = planet.energy
    solar = planet.buildings["Solarkraftwerk"]

    print(planet, metall, kristall, solar, energy)

    for building in planet.buildings:
        # print(planet.buildings[building].id)
        if planet.buildings[building].in_construction:
            print(
                f"{planet.name}: sleeping due to construction of {building} until {datetime.datetime.now() + datetime.timedelta(0, planet.buildings[building].construction_finished_in_seconds)}")
            time.sleep(planet.buildings[building].construction_finished_in_seconds)
            return

    if metall.level - kristall.level > 2:
        if int(kristall.energy_consumption_nxt_level) >= int(energy):
            if solar.is_possible:
                solar.build()
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "kristall_energy_sleep", "energy.is_possible:", solar.is_possible)
                time.sleep(60 * wait_factor)  # todo: calculate time until production is possible and run again
                return
        if kristall.is_possible:
            kristall.build()
            time.sleep(kristall.construction_time)
            return
        else:
            print(planet.name, "kristall_sleep", "kristall.is_possible:", kristall.is_possible)
            time.sleep(60 * wait_factor)  # todo: calculate time until production is possible and run again
            return
    if (metall.level - kristall.level) <= 2:
        if metall.energy_consumption_nxt_level >= energy:
            if solar.is_possible:
                solar.build()
                time.sleep(solar.construction_time)
                return
            else:
                print(planet.name, "metall_energy_sleep", "energy.is_possible:", solar.is_possible)
                time.sleep(60 * wait_factor)  # todo: calculate time until production is possible and run again
                return
        if metall.is_possible:
            metall.build()
            time.sleep(metall.construction_time)
            return
        else:
            print(planet.name, "metall_sleep", "metall.is_possible:", metall.is_possible)
            time.sleep(60 * wait_factor)  # todo: calculate time until production is possible and run again
            return


def thread_building(planet):
    print("Starting Thread...")
    while True:
        try:
            # todo: before new check - update buildings & energy
            planet.reader.read_all()
            build_next(planet)
        except AttributeError as e:
            print("No longer logged in", e)
            traceback.print_exc()
            a1.login()
            pass
        except Exception as e:
            print("Not sure what happened", e)
            traceback.print_exc()


wait_factor = 5
a1 = Account("Octans", "david-achilles@hotmail.de", "OGame!4friends")
a1.read_in_all_planets()
for i, planet in enumerate(a1.planets):
    print(i, planet)

# p0 = a1.planets[0]
# p1 = a1.planets[1]
# p2 = a1.planets[2]
# p3 = a1.planets[3]
# p4 = a1.planets[4]
#
# thread_building(p4)

with ThreadPoolExecutor() as executor:
    for i in range(len(a1.planets)):
        executor.submit(thread_building, a1.planets[i])

print("Done...")
