import re

import jsonpickle

from Account import *
from Resources import Resources


def getSoup(driver):
    # Get current Soup
    html = driver.page_source
    return BeautifulSoup(html, features="html.parser")


class Planet:
    def __init__(self, driver):
        time.sleep(2)
        #todo: Wenn Klasse Spieleraccount angelegt - mitgeben für uni Nr & Sprache
        driver.get(f"https://s167-de.ogame.gameforge.com/game/index.php?page=ingame&component=overview")

        self.link = driver.current_url
        # get Links
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

        # ID
        try:
            regexID = re.search("cp=\d*", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
            regexID = regexID.replace("cp=","")
            self.id = regexID
        except AttributeError as e:
            print("Attribute ID not found.",e)

        # Fields
        try:
            regexFields = re.search("\(\d*\/\d*\)", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
            regexFields = regexFields.replace("(", "").replace(")", "").split("/")
            if regexFields:
                self.fieldsMax = regexFields[1]
                self.fieldsUsed = regexFields[0]
        except AttributeError as e:
            print("Attribute Field not found.",e)

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
            print("Attribute Temperature not set.",e)

        # Resources
        try:
            metal = soup.find("span", {"id": "resources_metal"}).text
            crystal = soup.find("span", {"id": "resources_crystal"}).text
            deuterium = soup.find("span", {"id": "resources_deuterium"}).text
            self.resources = Resources(metal,crystal,deuterium)
        except AttributeError as e:
            print("Attribute Resources not found.",e)

        # Supplies (Buildings)
        try:
            driver.get(self.linkSupplies)
            soup = getSoup(driver)
            for li in soup.find_all("ul",{"id":"producers"}):
                for geb in li.find_all("li"):
                    print("loop:", geb,geb['aria-label'],geb['data-technology'])
        except:
            print("Error while creating Buildings of planet.")

        print("Created Planet:",jsonpickle.encode(self))

if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")
    p1 = Planet(a1.getDriver())

#
# soup = getSoup(driver)
# soup = soup.find("ul", {"id": "resources"})
# soup_metal = soup.find("li", {"id": "metal_box"})
# table = soup_metal.findChildren(['th', 'tr'])
# print(soup_metal)