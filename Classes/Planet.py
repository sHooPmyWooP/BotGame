import re

from bs4 import BeautifulSoup

from Classes.Building import Building
from Classes.Defense import Defense
from Classes.Resources import Resources
from Classes.Ship import Ship
from Classes.Coordinate import Coordinate, Destination


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
        self.temps = []  # min / max
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
                                                                                                               "").split("/")
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
                is_possible = True if 'data-status="on"' in building else False
                in_construction = True if 'data-status="active"' in building else False
                construction_finished_in_seconds = int(building["data-total"]) if in_construction else 0
                self.planet.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                         building['data-technology'],
                                                                         building.text, "facilities", is_possible,
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
            self.planet.ships[ship['aria-label']] = Ship(ship['aria-label'], ship['data-technology'],
                                                         ship.text, self)

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
