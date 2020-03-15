import pause

from Classes.Account import Account
from Classes.Coordinate import Coordinate
from Resources.Static_Information.Constants import mission_type_ids


def start_expo(planet):
    possible_expos = (planet.acc.expo_count[1] - planet.acc.expo_count[0])

    if planet.acc.expo_count[1] == 0:
        return  # no expo slots available yet
    if possible_expos < 1:
        return_times = []
        for mission in planet.acc.missions:
            if planet.acc.missions[mission]["return_flight"] and planet.acc.missions[mission][
                "mission-type"] == mission_type_ids.expedition:
                return_times.append(planet.acc.missions[mission]["timestamp_arrival"])
        earliest_start = min(dt for dt in return_times)
        print("sleep until:", earliest_start)
        pause.until(earliest_start)
        return

    big_t = planet.ships["Großer Transporter"]
    big_t_count = int(big_t.count / possible_expos)
    small_t = planet.ships["Kleiner Transporter"]
    small_t_count = int(small_t.count / possible_expos)
    pathfinder = planet.ships["Pathfinder"]
    pathfinder_count = 1 if int(pathfinder.count) > 0 else 0

    ships = [[big_t.id, big_t_count], [small_t.id, small_t_count], [pathfinder.id, pathfinder_count]]
    for _ in range(possible_expos):
        planet.send_fleet(mission_type_ids.expedition, Coordinate(1, 412, 16), ships, resources=[0, 0, 0], speed=10,
                          holdingtime=1)


def thread_expos(planet):
    print("Starting Thread...")
    while True:
        # todo: before new check - update buildings & energy
        a1.check_fleet_slots()
        start_expo(planet)


a1 = Account("Octans", "david-achilles@hotmail.de", "OGame!4friends")
a1.get_planet_ids()
a1.read_in_planet(a1.planet_ids[0])

thread_expos(a1.planets[0])
# with ThreadPoolExecutor() as executor:
#     expo1 = executor.submit(thread_expos, a1.planets[0])

print("Done...")
