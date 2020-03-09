import re
import time
import requests

class Building:

    def __init__(self, name, wfid, level, building_type, planet):
        self.name = name
        self.id = wfid
        self.level = int(level)
        self.type = building_type
        self.planet = planet

    def get_name(self):
        return self.name

    def upgrade(self):
        """
        upgrade building
        todo: not working by now
        :return: True on success
        """
        driver = self.planet.acc.driver
        self.level += 1

        # Determine URL
        if self.type == "facilities":
            link = self.planet.linkFacilities
        elif self.type == "supplies":
            link = self.planet.linkSupplies
            print("Upgrade supplies")
        else:
            print("No such building_type", self.type)
            return False

        # Go To Supplies/Facilities Page
        time.sleep(1)
        driver.get(link)
        # print(2,link)
        # time.sleep(1)
        # soup = self.planet.acc.getSoup()
        #
        # # Get Upgrade Link
        # soup = soup.find("li", {"data-technology": self.id})
        # link = re.search(pattern='(data-target=\".*?\")', string=str(soup))
        # link = re.search(pattern='\".*\"', string=str(link.group(0)))
        # link = link.group(0).replace('"', '')
        #
        # # Push the button and Trigger Upgrade
        # print(link)
        # requests.get(link)
        # driver.get(link)
        print("Upgrade done...")
        return True
