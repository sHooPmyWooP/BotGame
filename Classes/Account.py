import re

import requests
from bs4 import BeautifulSoup

from Classes.Message import SpyMessage
from Classes.OGame_API import OGameAPI
from Classes.Planet import Planet
from Classes.Research import Research


class Account:

    def __init__(self, universe, username, password, user_agent=None, proxy=''):
        # todo: get class (e.g. for expo)
        self.universe = universe
        self.username = username
        self.password = password
        self.chat_token = None
        self.sendfleet_token = None
        self.build_token = None
        self.session = requests.Session()
        self.session.proxies.update({'https': proxy})
        self.server_id = None
        self.server_number = None
        self.server_language = None
        self.server_name = ""
        self.server_settings = {}
        self.planets = []
        self.research = {}
        self.ogame_api = None
        self.spy_messages = {}

        if user_agent is None:
            user_agent = {
                'User-Agent':
                    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/80.0.3987.100 Mobile Safari/537.36'}
        self.session.headers.update(user_agent)
        self.universes = []

        self.login()

    def login(self):
        self.planets = []  # planets get appended to the list
        print("Start login...")
        form_data = {'kid': '',
                     'language': 'en',
                     'autologin': 'false',
                     'credentials[email]': self.username,
                     'credentials[password]': self.password}
        logged = self.session.post('https://lobby.ogame.gameforge.com/api/users', data=form_data)
        servers = self.session.get('https://lobby.ogame.gameforge.com/api/servers').json()
        for server in servers:
            if server['name'] == self.universe:
                self.server_number = server['number']
                break
        accounts = self.session.get('https://lobby.ogame.gameforge.com/api/users/me/accounts').json()
        for account in accounts:
            if account['server']['number'] == self.server_number:
                self.server_id = account['id']
                self.server_language = account['server']['language']
        login_link = self.session.get('https://lobby.ogame.gameforge.com/api/users/me/loginLink?'
                                      'id={}'
                                      '&server[language]={}'
                                      '&server[number]={}'
                                      '&clickedButton=account_list'.format(self.server_id,
                                                                           self.server_language,
                                                                           self.server_number)).json()
        self.session.content = self.session.get(login_link['url']).text

        # get Server info
        for server in self.session.get("https://lobby.ogame.gameforge.com/api/servers").json():
            if self.server_number == server["number"]:
                self.server_name = server["name"]
                for key in server["settings"]:
                    self.server_settings[key] = server["settings"][key]
                break
        self.get_ogame_api()  # API to get Players/Planets

    def read_in_researches(self):
        response = self.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                    'component=research&cp={}'
                                    .format(self.server_number, self.server_language,
                                            self.planets[0].id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"id": 'technologies'}):
            for research in result.find_all("li", {"class": "technology"}):
                is_possible = True if 'data-status="on"' in research else False
                in_construction = True if 'data-status="active"' in research else False
                level_str_list = re.findall('\d+', research.text)  # avoid problem with Bonus (4+3)
                level_sum = sum([int(val) for val in level_str_list])  # sum up vals from list ['4','3']
                self.research[research['aria-label']] = Research(name=research['aria-label'],
                                                                 id=research['data-technology'],
                                                                 level=level_sum,
                                                                 is_possible=is_possible,
                                                                 in_construction=in_construction)

    def read_in_all_planets(self):
        for planetId in self.get_planet_ids():
            planet = Planet(self, planetId)
            planet.reader.read_all()
            self.planets.append(planet)
            print('Planet ' + planet.name + ' with id ' + str(planet.id) + ' was added')

    def read_in_planet(self, planetId):
        planet = Planet(self, planetId)
        planet.reader.read_all()
        return self.planets.append(planet)

    def get_planet_ids(self):
        planet_ids = []
        marker_string = 'id="planet-'
        for planet_id in re.finditer(marker_string, self.session.content):
            id = self.session.content[planet_id.start() + 11:planet_id.end() + 8]
            planet_ids.append(int(id))
        return planet_ids

    def get_init_chat_token(self):
        marker_string = 'var ajaxChatToken = '
        for re_obj in re.finditer(marker_string, self.session.content):
            self.chat_token = self.session.content[re_obj.start() + len(marker_string): re_obj.end() + 35].split('"')[1]

    def get_init_sendfleet_token(self, content):
        marker_string = 'var fleetSendingToken = '
        for re_obj in re.finditer(marker_string, content):
            self.sendfleet_token = content[re_obj.start() + len(marker_string): re_obj.end() + 35].split('"')[1]

    def get_ogame_api(self):
        self.ogame_api = OGameAPI(self.server_number, self.server_language)

    def get_spy_messages(self, tab=20):
        """
        read messages from spy-inbox.
        :param tab: int (Representing the OGame internal ID for different Inboxes.
        -> 20: Spy, 21: Fight, 22: Expedition, 23: Transport, 24: Other...
        :return: None
        """

        response = self.session.get(
            f"https://s{self.server_number}-{self.server_language}.ogame.gameforge.com/game/index.php?page=messages&tab={tab}&ajax=1").text
        soup = BeautifulSoup(response, features="html.parser")
        for msg in soup.findAll("li", {"class": 'msg'}):
            if msg["data-msg-id"] not in self.spy_messages:
                self.spy_messages[msg["data-msg-id"]] = SpyMessage(self, msg)


if __name__ == "__main__":
    a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")
    a1.get_messages(20)
    print("Done...")
