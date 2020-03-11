import os
import re

from Classes.Resources import Resources


class Building:

    def __init__(self, name, id, level, building_type, is_possible, in_construction, planet):
        self.name = name
        self.id = id
        self.level = int(level)
        self.type = building_type
        self.planet = planet
        self.is_possible = is_possible
        self.in_construction = in_construction
        self.construction_time = 0
        self.construction_cost = Resources()
        self.energy_consumption = 0

    def __repr__(self):
        return self.name + ": " + str(self.level)

    def get_name(self):
        return self.name

    def set_construction_time(self):
        robo = self.planet.buildings["Roboterfabrik"]
        nanite = self.planet.buildings["Nanitenfabrik"]
        self.construction_time = int(((self.construction_cost.get_metal() + self.construction_cost.get_crystal()) / (
                2500 * (1 + robo.level) * self.planet.acc.server_settings[
            "economySpeed"] * 2 ** nanite.level)) * 60 * 60) + 1  # hours to seconds

    def set_construction_cost(self):
        cur_path = os.path.dirname(__file__)
        new_path = os.path.relpath('BotGame\Resources\Static_Information\Building_Base_Info', cur_path)
        with open(new_path, "r") as f:
            next(f)
            for line in f:
                line = line.split("|")
                if line[1] == self.id:
                    line_float = [float(x) for x in line[2:]]
                    base_factor, base_metal, base_crystal, base_deut, energy_factor, base_energy = line_float[:]
                    cost_metal = int(base_metal * base_factor ** self.level)
                    cost_crystal = int(base_crystal * base_factor ** self.level)
                    cost_deut = int(base_deut * base_factor ** self.level)
                    self.construction_cost = Resources(cost_metal, cost_crystal, cost_deut)
                    print("base_energy",base_energy, "self.level", self.level, "energy_factor",energy_factor)
                    self.energy_consumption = (base_energy * self.level * energy_factor ** self.level)
                    print("self.energy_consumption",self.energy_consumption)

    def build(self, amount=1):
        type = self.id
        component = self.type
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component={}&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       component, self.planet.id)).text
        self.get_init_build_token(response, component)

        build_url = 'https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&' \
                    'component={}&modus=1&token={}&type={}&menge={}' \
            .format(self.planet.acc.server_number, self.planet.acc.server_language, component,
                    self.planet.acc.build_token, type, amount)
        response = self.planet.acc.session.get(build_url)
        # self.planet.set_supply_buildings()
        print(self.name + " has been built on " + self.planet.name)
        self.set_construction_cost()
        self.set_construction_time()
        self.level += 1

    def get_init_build_token(self, content, component):
        marker_string = 'component={}&modus=1&token='.format(component)
        for re_obj in re.finditer(marker_string, content):
            self.planet.acc.build_token = content[re_obj.start() + len(marker_string): re_obj.end() + 32]
