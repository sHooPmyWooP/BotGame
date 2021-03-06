import datetime
import os
import re

"""sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi"""
from .Resources import Resources


class Building:
    """
    represents one Building (incl. supply & facility) with relation to one planet
    """

    def __init__(self, name, id, level, building_type, is_possible, in_construction, construction_finished_in_seconds,
                 celestial):
        """
        :param name: str
        :param id: int
        :param level: int
        :param building_type: str (hardcoded in planet)
        :param is_possible: bool
        :param in_construction: bool
        :param construction_finished_in_seconds: int
        :param celestial: Planet or Moon
        """
        self.name = name
        self.id = id
        self.level = int(level)
        self.type = building_type
        self.celestial = celestial
        self.is_possible = is_possible
        self.in_construction = in_construction
        self.construction_time = 0
        self.construction_cost = Resources()
        self.construction_finished_in_seconds = construction_finished_in_seconds
        self.energy_consumption_total = 0
        self.energy_consumption_nxt_level = 0

    def __repr__(self):
        return self.name + ": " + str(self.level)

    def get_name(self):
        return self.name

    def set_construction_time(self):
        """
        Calculate construction time of build
        :return: None
        """
        robo = self.celestial.buildings["Roboterfabrik"]
        nanite_level = 0 if self.celestial.is_moon else self.celestial.buildings["Nanitenfabrik"].level
        self.construction_time = int(((self.construction_cost.get_metal() + self.construction_cost.get_crystal()) / (
                2500 * (1 + robo.level) * self.celestial.acc.server_settings[
            "economySpeed"] * 2 ** nanite_level)) * 60 * 60) + 1  # hours to seconds

    def set_construction_cost(self):
        """
        Calculate construction costs & required Energy after the build
        :return:
        """
        path_building_base = os.path.abspath('../Resources/Static_Information/Building_Base_Info')
        with open(path_building_base, "r") as f:
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
                    try:
                        self.energy_consumption_total = (base_energy * self.level * energy_factor ** self.level)
                        self.energy_consumption_nxt_level = (base_energy * (self.level + 1) * energy_factor ** (
                                self.level + 1)) - self.energy_consumption_total
                    except ZeroDivisionError:
                        self.energy_consumption_total = 0
                        self.energy_consumption_nxt_level = 0

    def build(self, amount=1):
        """
        Upgrade Building to next level
        :param amount: int (default 1)
        :return: None
        """
        type = self.id
        component = self.type
        response = self.celestial.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                                  'component={}&cp={}'
                                                  .format(self.celestial.acc.server_number,
                                                          self.celestial.acc.server_language,
                                                          component, self.celestial.id)).text
        self.get_init_build_token(response, component)

        build_url = 'https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&' \
                    'component={}&modus=1&token={}&type={}&menge={}' \
            .format(self.celestial.acc.server_number, self.celestial.acc.server_language, component,
                    self.celestial.acc.build_token, type, amount)
        response = self.celestial.acc.session.get(build_url)
        self.set_construction_cost()
        self.set_construction_time()
        print(self.name + " has been built on " + self.celestial.name + " " + str(self.level) + " to " + str(
            self.level + 1) + " sleep until " + str(
            datetime.datetime.now() + datetime.timedelta(0, self.construction_time)))
        self.level += 1

    def get_init_build_token(self, content, component):
        """
        necessary to process build method
        :param content: str (response)
        :param component: str (supply/facility)
        :return:
        """
        marker_string = 'component={}&modus=1&token='.format(component)
        for re_obj in re.finditer(marker_string, content):
            self.celestial.acc.build_token = content[re_obj.start() + len(marker_string): re_obj.end() + 32]
