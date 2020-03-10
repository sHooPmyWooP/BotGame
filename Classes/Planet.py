import re

from bs4 import BeautifulSoup

from Classes.Building import Building
from Classes.Defense import Defense
from Classes.Resources import Resources
from Classes.Ship import Ship


class Planet:
    def __init__(self, acc, id):
        self.acc = acc
        self.buildings = {}
        self.ships = {}
        self.defenses = {}
        self.id = id
        self.coordinates = [0, 0, 0]
        self.fields = [0, 0]  # used / total
        self.temps = []  # min / max
        self.resources = Resources()
        self.energy = 0

        #####
        # Overview
        #####
        response = acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                   'page=ingame&component=overview'
                                   .format(acc.server_number, acc.server_language)).text
        soup = BeautifulSoup(response, features="html.parser")

        for result in soup.findAll("div", {"id": 'planet-' + str(self.id)}):
            # Coordinates
            for coord in result.findAll("span", {"class": "planet-koords"}):
                coord = coord.text.split(":")
                for i, x in enumerate(coord):
                    self.coordinates[i] = x.replace("[", "").replace("]", "")
            # Name
            for name in result.findAll("img", {"class": "planetPic"}):
                self.name = name["alt"]
            # Fields
            for res in result.findAll("a", {"class": "planetlink"}):
                self.fields = re.search("\(\d*\/\d*\)", res["title"]).group(0).replace("(", "").replace(")", "").split(
                    "/")
            # Temperature
            for res in result.findAll("a", {"class": "planetlink"}):
                temp = re.search("\d+ °C [a-zA-Z]* \d+", res["title"]).group(0)
                temp = re.findall("\d+", temp)
                self.temps = temp

        #####
        # Resources (on the Planet)
        #####
        response = self.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=resourceSettings&cp={}'
                                        .format(self.acc.server_number, self.acc.server_language, self.id)).text
        resources_names = ['metal', 'crystal', 'deuterium']
        for name in resources_names:
            marker_string = '<span id="resources_{}" data-raw='.format(name)
            value = int(response.split(marker_string)[1].split('>')[1].split('<')[0].split(',')[0].replace('.', ''))
            self.resources.set_value(value, name)

        # Energy
        marker_string = '<span id="resources_energy" data-raw='
        value = int(response.split(marker_string)[1].split('>')[1].split('<')[0].split(',')[0].replace('.', ''))
        self.energy = value

        #####
        # Supply Buildings
        #####
        response = self.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                        'component=supplies&cp={}'
                                        .format(self.acc.server_number, self.acc.server_language, id)).text
        soup = BeautifulSoup(response, features="html.parser")

        for result in soup.findAll("ul", {"id": 'producers'}):
            for building in result.findAll("li", {"class": "technology"}):
                is_possible = True if 'data-status="on"' in building else False
                in_construction = True if 'data-status="active"' in building else False
                self.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                  building['data-technology'],
                                                                  building.text, "supplies", is_possible,
                                                                  in_construction, self)

        #####
        # Facility Buildings
        #####
        response = self.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                        'component=facilities&cp={}'
                                        .format(self.acc.server_number, self.acc.server_language, self.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"id": 'technologies'}):
            for building in result.findAll("li", {"class": "technology"}):
                is_possible = True if 'data-status="on"' in building else False
                in_construction = True if 'data-status="active"' in building else False
                self.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                  building['data-technology'],
                                                                  building.text, "facilities", is_possible,
                                                                  in_construction, self)

        #####
        # Ships (on the Planet)
        #####

        response = self.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                        'component=shipyard&cp={}'
                                        .format(self.acc.server_number, self.acc.server_language, id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for ship in soup.find_all("li", {"class": "technology"}):
            self.ships[ship['aria-label']] = Ship(ship['aria-label'], ship['data-technology'],
                                                  ship.text, self)
        #####
        # Defense (on the Planet)
        #####

        response = self.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                        'component=defenses&cp={}'
                                        .format(self.acc.server_number, self.acc.server_language, id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"id": 'technologies'}):
            for defense in result.find_all("li", {"class": "technology"}):
                self.defenses[defense['aria-label']] = Defense(defense['aria-label'], defense['data-technology'],
                                                               defense.text, self)

        #####
        # Building Construction Costs & Times
        #####
        for building in self.buildings:
            self.buildings[building].set_construction_cost()
            self.buildings[building].set_construction_time()
