from bs4 import BeautifulSoup
import re
from Resources import Resources
from Account import *

target = "https://lobby.ogame.gameforge.com/de_DE/"

def getSoup(driver):
    # Get current Soup
    html = driver.page_source
    return BeautifulSoup(html, features="html.parser")


class Planet:
    def __init__(self, link, driver):
        self.link = link
        # get Links
        self.linkOverview = re.sub("component=\w*", "component=overview", link)
        self.linkSupplies = re.sub("component=\w*", "component=supplies", link)
        self.linkFacilities = re.sub("component=\w*", "component=facilities", link)
        self.linkShipyard = re.sub("component=\w*", "component=shipyard", link)
        self.linkDefenses = re.sub("component=\w*", "component=defenses", link)
        self.linkFleet = re.sub("component=\w*", "component=fleetdispatch", link)
        self.linkGalaxy = re.sub("component=\w*", "component=galaxy", link)

        #####
        # Overview
        #####
        driver.get(self.linkOverview)
        soup = getSoup(driver)

        # ID
        regexID = re.search("cp=\d*", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
        if regexID:
            self.id = regexID

        # Fields
        regexFields = re.search("\(\d*\/\d*\)", str(soup.findAll("a", {"class": "planetlink"}))).group(0)
        regexFields = regexFields.replace("(", "").replace(")", "").split("/")
        if regexFields:
            self.fieldsMax = regexFields[1]
            self.fieldsUsed = regexFields[0]

        # Temperature
        regexTemperature = re.findall("\d* °", str(soup.findAll("a", {"class": "planetlink"})))
        temps = []
        for temp in regexTemperature:
            temp = temp.replace("°", "")
            temp = temp.strip()
            temps.append(temp)
        self.tempMax = max(temps)
        self.tempMin = min(temps)

        # Resources
        metal = soup.find("span", {"id": "resources_metal"}).text
        crystal = soup.find("span", {"id": "resources_crystal"}).text
        deuterium = soup.find("span", {"id": "resources_deuterium"}).text
        self.resources = Resources(metal,crystal,deuterium)
        print("metal:", metal, "\ncrystal:", crystal, "\ndeut:", deuterium)
        # Todo : Lagerkapazität - ggf. Produktion


if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")
    #p1 = Planet("https://s167-de.ogame.gameforge.com/game/index.php?page=ingame&component=overview", a1.getDriver())

#
# soup = getSoup(driver)
# soup = soup.find("ul", {"id": "resources"})
# soup_metal = soup.find("li", {"id": "metal_box"})
# table = soup_metal.findChildren(['th', 'tr'])
# print(soup_metal)