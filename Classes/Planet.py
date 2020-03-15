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
            # print(self.name,self.buildings[building].name,self.buildings[building].level,self.buildings[building].construction_finished_in_seconds)

    def __repr__(self):
        return self.name + " id:" + str(self.id)

    def send_fleet(self, mission_id, coords, ships, resources=[0, 0, 0], speed=10, holdingtime=0):
        """
        :param mission_id:
        :param coords:
        :param ships: [[id,amount],[id,amount]]
        :param resources: int
        :param speed: int
        :param holdingtime: int # min 1 for expedition
        :return:
        """
        # ships = [["Ship_Name", "Amount"],...]
        response = self.acc.session.get(
            f'https://s{self.acc.server_number}-{self.acc.server_language}.ogame.gameforge.com/game/index.php?page=ingame&component=fleetdispatch&cp={self.id}').text
        self.acc.get_init_sendfleet_token(response)
        form_data = {'token': self.acc.sendfleet_token}

        for ship in ships:
            ship_type = f'am{ship[0]}'
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
        print("Mission started:", mission_id, ships, coords)
        print(response)
        return response['success']


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
        for name in resources_names:
            marker_string = '<span id="resources_{}" data-raw='.format(name)
            try:
                value = int(response.split(marker_string)[1].split('>')[1].split('<')[0].split(',')[0].replace('.', ''))
                self.planet.resources.set_value(value, name)
            except IndexError:
                print(self.planet.name, name)
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
