import re
from datetime import datetime

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
        self.planet_ids = []
        self.expo_count = [0, 0]  # current/max
        self.fleet_count = [0, 0]  # current/max
        self.offers_count = [0, 0]  # current/max
        self.missions = {}  # mission id +1 for return flight

        if user_agent is None:
            user_agent = {
                'User-Agent':
                    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/80.0.3987.100 Mobile Safari/537.36'}
        self.session.headers.update(user_agent)

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

    def read_in_mission_count(self):
        response = self.session.get(
            f'https://s{self.server_number}-{self.server_language}.ogame.gameforge.com/game/index.php?page=ingame&component=fleetdispatch').text  # &cp={self.planets[0].id entfernt
        soup = BeautifulSoup(response, features="html.parser")
        for result in soup.findAll("div", {"class": 'fleetStatus'}):
            for span in result.find_all("span"):
                #  Fleet
                marker_string_fleet = "Flotten:((?s).*)\d+/\d+"  # (?s) to match newlines as well
                regex_fleet = re.search(marker_string_fleet, str(span))
                try:
                    fleet_list = re.findall("\d+", regex_fleet.group(0))
                    self.fleet_count[0] = int(fleet_list[0])
                    self.fleet_count[1] = int(fleet_list[1])
                except AttributeError:  # this is not the span we're looking for
                    pass
                #  Expo
                marker_string_expo = "Expeditionen:((?s).*)\d+/\d+"  # (?s) to match newlines as well
                regex_expo = re.search(marker_string_expo, str(span))
                try:
                    expo_list = re.findall("\d+", regex_expo.group(0))
                    self.expo_count[0] = int(expo_list[0])
                    self.expo_count[1] = int(expo_list[1])
                except AttributeError:  # this is not the span we're looking for
                    pass
                #  Offers
                marker_string_offers = "Angebote:((?s).*)\d+/\d+"  # (?s) to match newlines as well
                regex_offers = re.search(marker_string_offers, str(span))
                try:
                    offers_list = re.findall("\d+", regex_offers.group(0))
                    self.offers_count[0] = int(offers_list[0])
                    self.offers_count[1] = int(offers_list[1])
                except AttributeError:  # this is not the span we're looking for
                    pass

    def check_fleet_slots(self):
        """
        read fleet slots with mission type, date of arrival/return and if return flight
        :return:
        """
        self.read_in_mission_count()
        response = self.session.get(
            f'https://s{self.server_number}-{self.server_language}.ogame.gameforge.com/game/index.php?page=ingame&component=movement').text
        soup = BeautifulSoup(response, features="html.parser")

        self.missions = {}
        for result in soup.find_all("div", {"id": "eventListWrap"}):
            for tr in result.find_all("tr", {"class": "eventFleet"}):
                id = int(re.search("\d+", tr["id"]).group())
                return_flight = True if tr["data-return-flight"] == "true" else False
                self.missions[id] = {
                    "timestamp_arrival": datetime.fromtimestamp(int(tr["data-arrival-time"])),
                    "mission-type": int(tr["data-mission-type"]),
                    "return_flight": return_flight}

    def read_in_all_planets(self):
        for planetId in self.get_planet_ids():
            planet = Planet(self, planetId)
            planet.reader.read_all()
            self.planets.append(planet)
            print('Planet ' + planet.name + ' with id ' + str(planet.id) + ' was added')

    def read_in_planet(self, planetId):
        planet = Planet(self, planetId)
        planet.reader.read_all()
        self.planets.append(planet)
        print('Planet ' + planet.name + ' with id ' + str(planet.id) + ' was added')
        return planet  # hier nur append returnen? - Notiz falls Fehler auftreten

    def get_planet_ids(self):
        planet_ids = []
        marker_string = 'id="planet-'
        for planet_id in re.finditer(marker_string, self.session.content):
            id = self.session.content[planet_id.start() + 11:planet_id.end() + 8]
            planet_ids.append(int(id))
        self.planet_ids = planet_ids
        return planet_ids

    def read_in_all_fleets(self):
        for planet in self.planets:
            planet.reader.read_fleet()

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

    def chk_get_attacked(self):
        response = self.session.post('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                     'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1'
                                     .format(self.server_number, self.server_language),
                                     headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        print(response)
        if response['hostile'] > 0:
            return True
        else:
            return False

    def chk_get_neutral(self):
        response = self.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                    'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1'
                                    .format(self.server_number, self.server_language),
                                    headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        if response['neutral'] > 0:
            return True
        else:
            return False

if __name__ == "__main__":
    a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")

    print(a1.chk_get_attacked())
    print("Done...")
