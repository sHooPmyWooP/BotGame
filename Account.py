# Todo: Pfad in config verschieben - Config anlegen
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import requests
import time
import json
from Universe import Universe

pathChromedriver = os.path.dirname(os.path.realpath(__file__)) + r"/Resources/Driver/chromedriver.exe"


# server-api = https://lobby.ogame.gameforge.com/api/servers

def getSoup(driver):
    # Get current Soup
    html = driver.page_source
    return BeautifulSoup(html, features="html.parser")


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
        self.login_uni = ""
        self.driver = ""

    def login(self, uni_name):
        """
        todo: Select correct universe with uni_pos
        Login to certain universe, populate Account with Universe Objects
        :param self:
        :param uni_name:
        :return: True if successful, False on Error
        """
        try:
            self.driver = self.newChromeBrowser(pathChromedriver=pathChromedriver)
            self.driver.maximize_window()  # Selection of universe won't work if not fullscreen
            self.driver.get("https://lobby.ogame.gameforge.com/de_DE/")  # todo auslagern in Config
            btnEinloggenAuswahl = self.driver.find_element_by_xpath(
                '//*[@id="loginRegisterTabs"]/ul/li[1]')  # Einloggen vs. Registrieren Top
            btnEinloggenAuswahl.click()

            btnEinloggen = self.driver.find_element_by_xpath('// *[ @ id = "loginForm"] / p / button[1]')
            email = self.driver.find_element_by_name("email")
            password = self.driver.find_element_by_name("password")

            email.send_keys(self.accName)
            password.send_keys(self.accPW)
            btnEinloggen.click()  # login cookie is now set
            time.sleep(1)

            if self.create_universes_from_account_api(self.driver):
                print("Universes created.")
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

            self.soup_accounts = getSoup(self.driver)
            accounts_table = self.soup_accounts.find("div", {"class": "rt-table"})
            uni_pos = 1
            for row in accounts_table.findAll("div", {"class": 'server-name-cell'}):
                if row.text == self.login_uni.name:
                    break
                else:
                    uni_pos += 1

            btnLogin = self.driver.find_element_by_xpath(f'//*[@id="accountlist"]/div/div[1]/div[2]/div[{uni_pos}]/div/div[11]/button/span')
            btnLogin.click()

            print(
                f"Successful Login [{self.accName}] in Universe [{self.login_uni.name}]")
            return True
        except Exception as e:
            print("Login failed.", e)
            return False

    def create_universes_from_account_api(self, driver):
        # Account Basedata - creation of Universe
        # todo: Maybe solve per request? login problematic
        # request-account details unter https://lobby.ogame.gameforge.com/api/users/me/accounts
        driver.get("https://lobby.ogame.gameforge.com/api/users/me/accounts")
        accInfo = getSoup(driver).text
        self.json_acc = json.loads(accInfo)
        if (self.json_acc):
            for uni in self.json_acc:
                self.Universes.append(Universe(uni))
            return True
        return False

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


if __name__ == "__main__":
    a1 = Account("david-achilles@hotmail.de", "OGame!4friends")
    a1.login("Octans")

    print("Done...")
