import re

# import jsonpickle
import jsonpickle

from Account import *
from Resources import Resources
from Defense import Defense
from Building import Building
from Ship import Ship


class Planet:
    def __init__(self, id):
        self.buildings = {}
        self.ships = {}
        self.defenses = {}
        self.id = id

        #####
        # Overview
        #####
        driver.get(self.linkOverview)
        soup = acc.getSoup()

        # Planet Name & Coordinate
        self.name = soup.find("span", {"id": "planetNameHeader"}).text.strip()  # strip due to spaces in html text
        coord = soup.find_all(text=re.compile('\[\d:\d*:\d\]'))
        self.coord = re.findall("\d{1,3}", coord[1])  # [x:xxx:x]-Format -> [x][xxx][x] todo: Make this a Coord Object

        # ID
        try:
            regexID = re.search("cp=\d*", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
            regexID = regexID.replace("cp=", "")
            self.id = regexID
        except AttributeError as e:
            print("Attribute ID not found.", e)

        # Fields
        try:
            regexFields = re.search("\(\d*\/\d*\)", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
            regexFields = regexFields.replace("(", "").replace(")", "").split("/")
            if regexFields:
                self.fieldsMax = regexFields[1]
                self.fieldsUsed = regexFields[0]
        except AttributeError as e:
            print("Attribute Field not found.", e)

        # Temperature
        try:
            regexTemperature = re.findall("\d* °", str(soup.findAll("a", {"class": "planetlink"})))
            temps = []
            for temp in regexTemperature:
                temp = temp.replace("°", "")
                temp = temp.strip()
                temps.append(temp)
            self.tempMax = max(temps)
            self.tempMin = min(temps)
        except AttributeError as e:
            print("Attribute Temperature not set.", e)

        # Resources
        try:
            metal = soup.find("span", {"id": "resources_metal"}).text
            crystal = soup.find("span", {"id": "resources_crystal"}).text
            deuterium = soup.find("span", {"id": "resources_deuterium"}).text
            self.resources = Resources(metal, crystal, deuterium)
        except AttributeError as e:
            print("Attribute Resources not found.", e)

        # Supplies (Buildings)
        try:
            driver.get(self.linkSupplies)
            soup = acc.getSoup()
            print(soup)
            print("--------")
            for li in soup.find_all("ul", {"id": "producers"}):
                print(li)
                for building in li.find_all("li"):
                    self.buildings[building['aria-label']] = Building(building['aria-label'],
                                                                      building['data-technology'],
                                                                      building.text, "supplies", self)
        except:
            print("Error while creating Buildings of planet.")

        # Facilities
        try:
            driver.get(self.linkFacilities)
            soup = acc.getSoup()
            soupFacility = soup.find("div", {"id": "technologies"})
            for facility in soupFacility.find_all("li", {"class": "technology"}):
                self.buildings[facility['aria-label']] = Building(facility['aria-label'], facility['data-technology'],
                                                                  facility.text, "facilities", self)
        except Exception:
            print("Error while creating Facilities of planet.")

        # Shipyard
        try:
            driver.get(self.linkShipyard)
            soup = acc.getSoup()
            soupShipyard = soup.find("div", {"id": "technologies"})
            for ship in soupShipyard.find_all("li", {"class": "technology"}):
                self.ships[ship['aria-label']] = Ship(ship['aria-label'], ship['data-technology'],
                                                      ship.text, self)
        except Exception:
            print("Error while creating Shipyard of planet.")

        # Defense
        try:
            driver.get(self.linkDefenses)
            soup = acc.getSoup()
            soupDefenses = soup.find("div", {"id": "technologies"})
            for defense in soupDefenses.find_all("li", {"class": "technology"}):
                self.defenses[defense['aria-label']] = Defense(defense['aria-label'], defense['data-technology'],
                                                               defense.text, self)
        except Exception:
            print("Error while creating Shipyard of planet.")

        # print("Created Planet:", jsonpickle.encode(self))

    def get_next_building(self):
        with open(file=r"Resources\BuildOrders\BO_Start", mode="r") as f:
            next(f)
            for line in f:
                line = line.split(";")
                line[0] = line[0].strip()
                line[1] = int(line[1].strip())
                if self.buildings[line[0]].level < line[1]:
                    self.buildings[line[0]].upgrade()
                    return True
        print("no upgrade")
        return False


if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")
    p1 = Planet(a1)
    p1.get_next_building()
    # for building in p1.buildings:
    #     print(building.name, building.level)
    # a1.getDriver().close()
