import re

from bs4 import BeautifulSoup

from Classes.Building import Building
from Classes.Coordinate import Coordinate, Destination
from Classes.Defense import Defense
from Classes.Resources import Resources
from Classes.Ship import Ship


class Planet:
    """
    Represents one Planet with relation to one account.
    """

    def __init__(self, acc, id):
        """
        :param acc: Account (associated with the Planet)
        :param id: int (ID of the Planet)
        self.buildings = Dict of Buildings accessible e.g. as self.buildings["Metallmine"]
        self.ships = Dict of Ships accessible e.g. as self.ships["Kleiner Transporter"]
        self.defenses = Dict of Defenses accessible e.g. as self.defenses["Kleiner Transporter"]
        self.coordinates = [0, 0, 0]
        self.fields = used / total
        self.temps = []  # min / max
        self.resources = Resources()
        self.energy = 0
        """
        self.acc = acc
        self.buildings = {}
        self.ships = {}
        self.defenses = {}
        self.id = id
        self.coordinates = Coordinate(0, 0, 0, Destination.Planet)
        self.fields = [0, 0]  # used / total
        self.temperature = []  # min / max
        self.resources = Resources()
        self.energy = 0
        self.name = ""

        self.reader = PlanetReader(self)

        #####
        # Building Construction Costs & Times
        #####
        for building in self.buildings:
            self.buildings[building].set_construction_cost()
            self.buildings[building].set_construction_time()
            print(self.name, self.buildings[building].name, self.buildings[building].level,
                  self.buildings[building].construction_finished_in_seconds)

    def __repr__(self):
        return self.name + " id:" + str(self.id)

    def build_defense_routine(self, multiplier=1):
        """
        :param multiplier:
        :return:
        """

        if self.defenses["Kleine Schildkuppel"].count is 0 and self.defenses["Kleine Schildkuppel"].read_max_build():
            self.defenses["Kleine Schildkuppel"].build(1)

        if self.defenses["Große Schildkuppel"].count is 0 and self.defenses["Große Schildkuppel"].read_max_build():
            self.defenses["Große Schildkuppel"].build(1)

        path_defense_routine = r'Resources/BuildOrders/Defense_Routine'
        with open(path_defense_routine, "r", encoding="utf-8") as f:
            next(f)
            for line in f:
                line = line.split("|")
                if self.defenses[line[0]].read_max_build():
                    if int(line[1] * multiplier) <= self.defenses[line[0]].max_build:
                        self.defenses[line[0]].build(int(line[1] * multiplier))
                    else:
                        self.defenses[line[0]].build(self.defenses[line[0]].max_build)

    def send_fleet(self, mission_id, coords, ships, resources=[0, 0, 0], speed=10, holdingtime=0):
        """
        :param mission_id: type of mission
        :param coords: Coordinate()
        :param ships: [[Ship,amount],[Ship,amount]]
        :param resources: int
        :param speed: int
        :param holdingtime: int (1 for expeditions)
        """
        response = self.acc.session.get(
            f'https://s{self.acc.server_number}-{self.acc.server_language}.ogame.gameforge.com/game/index.php?page=ingame&component=fleetdispatch&cp={self.id}').text
        self.acc.get_init_sendfleet_token(response)
        form_data = {'token': self.acc.sendfleet_token}

        for ship in ships:
            ship_type = f'am{ship[0].id}'  # e.g. am201 is the OGame Format
            ship_amount = ship[1]
            form_data.update({ship_type: ship_amount})

        form_data.update({'galaxy': coords.galaxy,
                          'system': coords.system,
                          'position': coords.position,
                          'type': coords.destination,
                          'metal': resources[0],
                          'crystal': resources[1],
                          'deuterium': resources[2],
                          'prioMetal': 1,
                          'prioCrystal': 2,
                          'prioDeuterium': 3,
                          'mission': mission_id,
                          'speed': speed,
                          'retreatAfterDefenderRetreat': 0,
                          'union': 0,
                          'holdingtime': holdingtime})
        response = self.acc.session.post('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                         'component=fleetdispatch&action=sendFleet&ajax=1&asJson=1'
                                         .format(self.acc.server_number, self.acc.server_language), data=form_data,
                                         headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        if response["success"]:
            print(self.name, "Mission started:", mission_id,
                  ["ship:" + str(ship[0].name) + " amount:" + str(ship[1]) for ship in ships], coords)
        return response


class PlanetReader:
    def __init__(self, planet):
        self.planet = planet

    def read_all(self):
        self.read_planet_infos()
        self.read_resources_and_energy()
        self.read_supply_buildings()
        self.read_facility_buildings()
        self.read_fleet()
        self.read_defences()
        for building in self.planet.buildings:
            self.planet.buildings[building].set_construction_cost()
            self.planet.buildings[building].set_construction_time()

    def read_planet_infos(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                               'page=ingame&component=overview'
                                               .format(self.planet.acc.server_number,
                                                       self.planet.acc.server_language)).text
        soup = BeautifulSoup(response, features="html.parser")

        for result in soup.findAll("div", {"id": 'planet-' + str(self.planet.id)}):
            # Coordinates
            for coord in result.findAll("span", {"class": "planet-koords"}):
                coord = coord.text.split(":")

                for i, x in enumerate(coord):
                    coord[i] = x.replace("[", "").replace("]", "")

                self.planet.coordinates = Coordinate(coord[0], coord[1], coord[2], Destination.Planet)

            # Name
            for name in result.findAll("img", {"class": "planetPic"}):
                self.planet.name = name["alt"]
            # Fields
            for res in result.findAll("a", {"class": "planetlink"}):
                self.planet.fields = re.search("\(\d*\/\d*\)", res["title"]).group(0).replace("(", "").replace(")",
                                                                                                               "").split(
                    "/")
            # Temperature
            for res in result.findAll("a", {"class": "planetlink"}):
                temp = re.search("-?\d+ °C [a-zA-Z]* -?\d+", res["title"]).group(0)
                temp = re.findall("-?\d+", temp)
                self.planet.temps = temp

    def read_resources_and_energy(self):
        response = self.planet.acc.session.get(
            'https://s{}-{}.ogame.gameforge.com/game/index.php?page=resourceSettings&cp={}'
                .format(self.planet.acc.server_number, self.planet.acc.server_language, self.planet.id)).text
        resources_names = ['metal', 'crystal', 'deuterium']
        # soup = BeautifulSoup(response, features="html.parser")

        for name in resources_names:
            marker_string = '<span id="resources_{}" data-raw="\d+'.format(name)
            try:
                # print_st = soup.find("li",{"id":name+"_box"})
                # res = re.search("Lagerkapazität:((?s).*)\d+.?\d+",str(print_st))
                # print("regex",res.group(0))
                # soup_res = BeautifulSoup(print_st, features="html.parser")
                # for lager in soup_res.find_all("span",{"class":"overmark"}):
                #     print(lager)
                # marker_string2 =
                # print(print_st)
                value_string = re.search(marker_string, response).group(0)  # <span id="resources_{}" data-raw=12345
                value = int(re.search("\d+", value_string).group(0))  # 12345
                # value = int(response.split(marker_string)[1].split('>')[1].split('<')[0].split(',')[0].replace('.', ''))
                self.planet.resources.set_value(value, name)
            except IndexError as e:
                print(response)
                print(self.planet.name, name, e)
                pass  # Resource-Value = 0 and therefor not in string
        # Energy
        marker_string = '<span id="resources_energy" data-raw='
        value = int(response.split(marker_string)[1].split('>')[1].split('<')[0].split(',')[0].replace('.', ''))
        self.planet.energy = value

    def read_supply_buildings(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=supplies&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id)).text
        soup = BeautifulSoup(response, features="html.parser")

        for result in soup.findAll("ul", {"id": 'producers'}):
            for building in result.findAll("li", {"class": "technology"}):
                level_list = building.text.strip().split(" ")
                level = [x.replace(r"\n", "") for x in level_list]
                is_possible = True if building["data-status"] == "on" else False
                in_construction = True if building["data-status"] == "active" else False
                construction_finished_in_seconds = int(building["data-total"]) if in_construction else 0
                self.planet.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                         building['data-technology'],
                                                                         level[0], "supplies", is_possible,
                                                                         in_construction,
                                                                         construction_finished_in_seconds,
                                                                         self.planet)

    def read_facility_buildings(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=facilities&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"id": 'technologies'}):
            for building in result.findAll("li", {"class": "technology"}):
                level_list = building.text.strip().split(" ")
                level = [x.replace(r"\n", "") for x in level_list]
                is_possible = True if 'data-status="on"' in building else False
                in_construction = True if 'data-status="active"' in building else False
                construction_finished_in_seconds = int(building["data-total"]) if in_construction else 0
                self.planet.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                         building['data-technology'],
                                                                         level[0], "facilities", is_possible,
                                                                         in_construction,
                                                                         construction_finished_in_seconds,
                                                                         self.planet)

    def read_fleet(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=shipyard&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for ship in soup.find_all("li", {"class": "technology"}):
            try:
                count = int(ship.text)
            except ValueError:  # Ships currently build - refer to currently accessible amount
                count = ship.text.split("\n")[-1].strip()  # get last element of list
            self.planet.ships[ship['aria-label']] = Ship(ship['aria-label'], ship['data-technology'],
                                                         count, self)

    def read_defences(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=defenses&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"id": 'technologies'}):
            for defense in result.find_all("li", {"class": "technology"}):
                self.planet.defenses[defense['aria-label']] = Defense(defense['aria-label'], defense['data-technology'],
                                                                      defense.text, self.planet)