import re

# import jsonpickle

from Account import *
from Resources import Resources
import Defense, Building, Ship


def getSoup(driver):
    # Get current Soup
    html = driver.page_source
    return BeautifulSoup(html, features="html.parser")


class Planet:
    def __init__(self, acc):
        driver = acc.getDriver()
        # todo: Wenn Klasse Spieleraccount angelegt - mitgeben für uniNr, Sprache & driver (acc ersetzen) (Statt Account)
        self.acc = acc
        self.buildings = {}
        self.ships = {}
        self.defenses = {}

        # get Links
        time.sleep(2)  # w/o sleep loading page will be captured
        driver.get(f"https://s167-de.ogame.gameforge.com/game/index.php?page=ingame&component=overview")
        self.link = driver.current_url
        self.linkOverview = re.sub("component=\w*", "component=overview", self.link)
        self.linkSupplies = re.sub("component=\w*", "component=supplies", self.link)
        self.linkFacilities = re.sub("component=\w*", "component=facilities", self.link)
        self.linkShipyard = re.sub("component=\w*", "component=shipyard", self.link)
        self.linkDefenses = re.sub("component=\w*", "component=defenses", self.link)
        self.linkFleet = re.sub("component=\w*", "component=fleetdispatch", self.link)
        self.linkGalaxy = re.sub("component=\w*", "component=galaxy", self.link)

        #####
        # Overview
        #####
        driver.get(self.linkOverview)
        soup = getSoup(driver)

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
            soup = getSoup(driver)
            for li in soup.find_all("ul", {"id": "producers"}):
                for building in li.find_all("li"):
                    self.buildings[building['aria-label']] = {"id": building['data-technology'], "level": building.text, "type": "supplies"}
                    # print("loop:", building['aria-label'], building['data-technology'], building.text)
                    # todo: Creation of Building Objects from building

        except:
            print("Error while creating Buildings of planet.")

        # Facilities
        try:
            driver.get(self.linkFacilities)
            soup = getSoup(driver)
            soupFacility = soup.find("div", {"id": "technologies"})
            for facility in soupFacility.find_all("li", {"class": "technology"}):
                self.buildings[facility['aria-label']] = {"id": facility['data-technology'], "level": facility.text,
                                                          "type": "facilities"}
                #print(facility['aria-label'], facility['data-technology'], facility.text)
                # todo: Creation of Facility Objects from facility
        except Exception:
            print("Error while creating Facilities of planet.")

        # Shipyard
        try:
            driver.get(self.linkShipyard)
            soup = getSoup(driver)
            soupShipyard = soup.find("div", {"id": "technologies"})
            for ship in soupShipyard.find_all("li", {"class": "technology"}):
                self.ships[ship['aria-label']] = {"id": ship['data-technology'], "count": ship.text}
        except Exception:
            print("Error while creating Shipyard of planet.")

        # Defense
        try:
            driver.get(self.linkDefenses)
            soup = getSoup(driver)
            soupDefenses = soup.find("div", {"id": "technologies"})
            for defense in soupDefenses.find_all("li", {"class": "technology"}):
                self.defenses[defense['aria-label']] = Defense(defense['aria-label'], defense['data-technology'], defense.text, self)
                # print(defense['aria-label'], defense['data-technology'], defense.text)  # todo:create defense Objects
        except Exception:
            print("Error while creating Shipyard of planet.")

        print(self.buildings)
        print(self.ships)
        print(self.defenses)
        # print("Created Planet:", jsonpickle.encode(self))


if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")
    p1 = Planet(a1)
    a1.getDriver().close()
#
# soup = getSoup(driver)
# soup = soup.find("ul", {"id": "resources"})
# soup_metal = soup.find("li", {"id": "metal_box"})
# table = soup_metal.findChildren(['th', 'tr'])
# print(soup_metal)
