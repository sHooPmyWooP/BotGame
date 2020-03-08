# Todo: Pfad in config verschieben - Config anlegen
import json
import os
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from Universe import Universe

# https://s167-de.ogame.gameforge.com/game/index.php?page=componentOnly&component=eventList&ajax=1 - Pfad merken für Ereignisse
pathChromedriver = os.path.dirname(os.path.realpath(__file__)) + r"/Resources/Driver/chromedriver.exe"


# server-api = https://lobby.ogame.gameforge.com/api/servers


class Account:
    """
    """

    def __init__(self, accName, accPW):
        """
        :param accName: str
        :param accPW:  str
        json_acc: JSON Return from Account API https://lobby.ogame.gameforge.com/api/users/me/accounts
        soup_accounts: str of soup from Universe selection page
        login_uni: Universe (currently active)
        """
        self.accName = accName
        self.accPW = accPW
        self.json_acc = ""
        self.Universes = []
        self.soup_accounts = ""
        self.login_uni = None
        self.driver = None
        self.overview_page = ""

    def login(self, uni_name):
        """
        Login to certain universe, populate Account with Universe Objects
        :param uni_name: str name of universe
        :return: True if successful, False on Error
        """
        try:
            self.driver = self.newChromeBrowser(pathChromedriver=pathChromedriver)
            self.driver.maximize_window()  # Selection of universe won't work if not fullscreen
            self.driver.get("https://lobby.ogame.gameforge.com/de_DE/")  # todo auslagern in Config
            btnEinloggenAuswahl = self.driver.find_element_by_xpath(
                '//*[@id="loginRegisterTabs"]/ul/li[1]')  # Login vs. Registrieren Top
            btnEinloggenAuswahl.click()

            btnEinloggen = self.driver.find_element_by_xpath('// *[ @ id = "loginForm"] / p / button[1]')
            email = self.driver.find_element_by_name("email")
            password = self.driver.find_element_by_name("password")

            email.send_keys(self.accName)
            password.send_keys(self.accPW)
            btnEinloggen.click()  # login cookie is now set
            time.sleep(1)

            if self.create_universes_from_account_api(self):
                print("All Universes created.")
            else:
                print("No active Universe identified after Login.")
                return False

            # Universe to login to
            for uni in self.Universes:
                if uni.name == uni_name:
                    self.login_uni = uni
                    break

            # Continue to Login - select Universe
            self.driver.get("https://lobby.ogame.gameforge.com/de_DE/accounts")  # Universe-Overview
            time.sleep(1)

            self.soup_accounts = self.getSoup()
            accounts_table = self.soup_accounts.find("div", {"class": "rt-table"})
            uni_pos = 1
            for row in accounts_table.findAll("div", {"class": 'server-name-cell'}):
                if row.text == self.login_uni.name:
                    break
                else:
                    uni_pos += 1

            btnLogin = self.driver.find_element_by_xpath(
                f'//*[@id="accountlist"]/div/div[1]/div[2]/div[{uni_pos}]/div/div[11]/button/span')
            btnLogin.click()

            time.sleep(2)
            if len(self.driver.window_handles[1])>1:
                self.driver.switch_to.window(self.driver.window_handles[1]) # Assuming after Login new Tab at Index 1
                # if a new Tab gets created
            self.overview_page = self.driver.current_url
            print(
                f"Successful Login [{self.accName}] in Universe [{self.login_uni.name}]")
            return True
        except NoSuchElementException as e:
            print("Element not found.",e, traceback.format_exc())
            return False
        except Exception as e:
            print("Login failed.", e)
            self.driver.close()
            return False

    def create_universes_from_account_api(self, driver):
        # Account Basedata - creation of Universe
        # todo: Maybe solve per request? login problematic
        # request-account details unter https://lobby.ogame.gameforge.com/api/users/me/accounts
        self.driver.get("https://lobby.ogame.gameforge.com/api/users/me/accounts")
        accInfo = self.getSoup().text
        self.json_acc = json.loads(accInfo)
        if self.json_acc:
            for uni in self.json_acc:
                self.Universes.append(Universe(self,uni))
            return True
        return False

    def account_init(self):
        # todo: Planeten aus Overview herauslesen und initialisieren. Methode in Player_Account verschieben wenn es die Klasse gibt
        driver = self.driver
        driver.get(self.overview_page)
        #print(self.overview_page)
        time.sleep(1)
        soup = self.getSoup()
        print(soup)


    @staticmethod
    def newChromeBrowser(pathChromedriver, headless=False, detach=True):
        """
        Helper function that creates a new Selenium browser
        pathChromedriver: str
        headless: bool (Browser visible)
        detach: bool (Browser stays open after code execution)
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        if (detach == True):
            options.add_experimental_option("detach", True)
        browser = webdriver.Chrome(options=options, executable_path=pathChromedriver)
        return browser

    def getDriver(self):
        return self.driver

    def getSoup(self):
        # Get current Soup
        html = self.driver.page_source
        return BeautifulSoup(html, features="html.parser")


if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")
    # a1.account_init()

    print("Done...")
