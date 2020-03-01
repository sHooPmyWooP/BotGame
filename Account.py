#Todo: Pfad in config verschieben - Config anlegen
pathChromedriver = r"C:\chromedriver.exe"
from selenium import webdriver

class Account:
    def __init__(self, accName, accPW):
        self.accName = accName
        self.accPW = accPW

    def login(self):
        driver = self.newChromeBrowser(pathChromedriver=pathChromedriver)
        driver.get("https://lobby.ogame.gameforge.com/de_DE/") #todo auslagern in Config
        btnEinloggenAuswahl = driver.find_element_by_xpath('//*[@id="loginRegisterTabs"]/ul/li[1]') #Einloggen vs. Registrieren Top
        btnEinloggenAuswahl.click()

        btnEinloggen = driver.find_element_by_xpath('// *[ @ id = "loginForm"] / p / button[1]')
        email = driver.find_element_by_name("email")
        password = driver.find_element_by_name("password")

        email.sendKeys(self.accName)
        password.sendKeys(self.accPW)
        btnEinloggen.click()

    @staticmethod
    def newChromeBrowser(pathChromedriver,headless=False, downloadPath=None):
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
    
a1 = Account("david-achilles@hotmail.de","OGame!4friends")
a1.login()