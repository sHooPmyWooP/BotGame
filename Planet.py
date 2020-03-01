from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
import re

target = "https://lobby.ogame.gameforge.com/de_DE/"

def newChromeBrowser(headless=True, downloadPath=None):
    """ Helper function that creates a new Selenium browser """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    if downloadPath is not None:
        prefs = {}
        if not os.path.exists(downloadPath):
            os.makedirs(downloadPath)
        prefs["profile.default_content_settings.popups"] = 0
        prefs["download.default_directory"] = downloadPath
        options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=options, executable_path=pathChromedriver)
    return browser


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
        # Todo: Resourcen in Klasse Resource
        metal = soup.find("span", {"id": "resources_metal"}).text
        crystal = soup.find("span", {"id": "resources_crystal"}).text
        deuterium = soup.find("span", {"id": "resources_deuterium"}).text
        print("metal:", metal, "\ncrystal:", crystal, "\ndeut:", deuterium)
        # Todo : Lagerkapazität - ggf. Produktion

p1 = Planet("https://s167-de.ogame.gameforge.com/game/index.php?page=ingame&component=overview", driver)

soup = getSoup(driver)
soup = soup.find("ul", {"id": "resources"})
soup_metal = soup.find("li", {"id": "metal_box"})
table = soup_metal.findChildren(['th', 'tr'])
print(soup_metal)