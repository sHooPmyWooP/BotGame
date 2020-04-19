import datetime
import json
import random
import re
import sys
import traceback
from os import path

import pause
import requests
from bs4 import BeautifulSoup

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi

try:  # Coordinate
    from .Coordinate import Coordinate
except ModuleNotFoundError:
    from Modules.Classes.Coordinate import Coordinate
except ImportError:
    from Modules.Classes.Coordinate import Coordinate
try:  # Resources
    from .Resources import Resources
except ModuleNotFoundError:
    from Modules.Classes.Resources import Resources
except ImportError:
    from Modules.Classes.Resources import Resources
try:  # SpyMessage
    from .Message import SpyMessage, ExpoMessage
except ModuleNotFoundError:
    from Modules.Classes.Message import SpyMessage, ExpoMessage
except ImportError:
    from Modules.Classes.Message import SpyMessage, ExpoMessage
try:  # Mission
    from .Mission import Mission
except ModuleNotFoundError:
    from Modules.Classes.Mission import Mission
except ImportError:
    from Modules.Classes.Mission import Mission
try:  # OGameAPI
    from .OGameAPI import OGameAPI
except ModuleNotFoundError:
    from Modules.Classes.OGameAPI import OGameAPI
except ImportError:
    from Modules.Classes.OGameAPI import OGameAPI
try:  # Celestial
    from .Celestial import Planet, Moon, Celestial
except ModuleNotFoundError:
    from Modules.Classes.Celestial import Planet, Moon, Celestial
except ImportError:
    from Modules.Classes.Celestial import Planet, Moon, Celestial
try:  # Research
    from .Research import Research
except ModuleNotFoundError:
    from Modules.Classes.Research import Research
except ImportError:
    from Modules.Classes.Research import Research
try:  # CustomExceptions
    from .CustomExceptions import NoShipsAvailableError
except ModuleNotFoundError:
    from Modules.Classes.CustomExceptions import NoShipsAvailableError
except ImportError:
    from Modules.Classes.CustomExceptions import NoShipsAvailableError

try:
    from Modules.Resources.Static_Information.Constants import mission_type_ids, static_lists
except ModuleNotFoundError:
    from Resources.Static_Information.Constants import mission_type_ids, ship_list


class Account:

    def __init__(self, universe, username, password, user_agent=None, proxy=''):
        # todo: get class (e.g. for expo)
        self.universe = universe
        self.username = username
        self.player_name = ''
        self.password = password
        self.AccountFunctions = AccountFunctions(self)
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
        self.moons = []
        self.research = {}
        self.ogame_api = None
        self.spy_messages = {}
        self.expo_messages = {}
        self.planet_ids = []
        self.moon_ids = []
        self.expo_count = [0, 0]  # current/max
        self.fleet_count = [0, 0]  # current/max
        self.offers_count = [0, 0]  # current/max
        self.missions = []

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
        # try:
        for account in accounts:
            if account['server']['number'] == self.server_number:
                self.server_id = account['id']
                self.player_name = account['name']
                self.server_language = account['server']['language']
        # except TypeError:
        #     print("No valid login information!")
        #     exit()
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

        print(f'Login user {self.player_name} in universe {self.server_name} successful')

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
        """
        sets current and maximum values for fleets, expos and offers in the format
        self.fleet_count[min,max]
        self.expo_count[min,max]
        self.offers_count[min,max]
        :return: None
        """
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

    def read_in_all_celestials(self, planets=True):
        """
        Read in all information for all celestials. If moons are included depends on parameter planets
        :param planets: Boolean - True if only planets should be read, includes moons otherwise
        :return:
        """
        ids = self.get_planet_ids() if planets else self.get_planet_ids() + self.get_moon_ids()
        for id in ids:
            celestial = Celestial(self, id)
            celestial.reader.read_all()
            self.planets.append(celestial) if not celestial.is_moon else self.moons.append(celestial)
            print(celestial.name + ' with id ' + str(celestial.id) + ' was added')

    def read_in_celestial(self, id):
        """
        Reads in a specific celestial which is identified by OGame internal ID
        :param id: int  - can be taken from html address in the format cp=12345678
        :return: Celestial
        """
        celestial = Celestial(self, id)
        celestial.reader.read_all()
        if not celestial.is_moon:
            self.planets.append(celestial)
        else:
            self.moons.append(celestial)
        print('Celestial ' + celestial.name + ' with id ' + str(celestial.id) + ' was added')
        return celestial

    def get_planet_ids(self):
        """
        Get all IDs of Planets
        :return: int[ ]
        """
        planet_ids = []
        marker_string = 'id="planet-'
        for planet_id in re.finditer(marker_string, self.session.content):
            id = self.session.content[planet_id.start() + 11:planet_id.end() + 8]
            planet_ids.append(int(id))
        self.planet_ids = planet_ids
        return planet_ids

    def get_moon_ids(self):
        """
        Get all IDs of Moons
        :return: int[ ]
        """
        moon_ids = []
        soup = BeautifulSoup(self.session.content, features="html.parser")
        moon_elements = soup.find_all("a", {"class": "moonlink"})
        for moon in moon_elements:
            id = re.search("cp=\d+", str(moon)).group(0).split("cp=")[1]
            moon_ids.append(int(id))
        self.moon_ids = moon_ids
        return moon_ids

    def init_celestials(self):
        """
        Initiates the celestials with base information ID, is_moon, coordinate, name, fields,
        temperature (planet only)
        """
        for id in self.get_planet_ids() + self.get_moon_ids():
            for celestial in self.planets + self.moons:
                if celestial.id == id:
                    break
            else:
                celestial = Celestial(self, id)
                celestial.reader.read_base_infos()
                self.planets.append(celestial) if not celestial.is_moon else self.moons.append(celestial)

    def get_celestial_by_coord(self, coord):
        """
        :param coord: Coordinate
        :return: Celestial
        """
        for celestial in self.moons + self.planets:
            if celestial.coordinates.get_coord_str() == coord.get_coord_str():
                return celestial

    def read_in_all_fleets(self):
        """
        Populate Ships{} for all Celestials
        """
        for planet in self.planets:
            planet.reader.read_fleet()
        for moon in self.moons:
            moon.reader.read_fleet()

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

    def get_expo_messages(self, tab=22):
        print('read expo messages from account')
        """
        read messages from spy-inbox.
        :param tab: int (Representing the OGame internal ID for different Inboxes.
        -> 20: Spy, 21: Fight, 22: Expedition, 23: Transport, 24: Other...
        :return: None
        """
        response = self.session.get(
            f"https://s{self.server_number}-{self.server_language}.ogame.gameforge.com/game/index.php?page=messages&tab={tab}&ajax=1").text
        soup = BeautifulSoup(response, features="html.parser")
        page_count = int(soup.find("li", {"class": "curPage"}).text.split("/")[1])
        for page in range(page_count):
            page += 1
            form_data = {
                "messageId": -1,
                "tabid": tab,
                "action": 107,
                "pagination": page,
                "ajax": 1
            }
            response = self.session.post(
                f'https://s{self.server_number}-{self.server_language}.ogame.gameforge.com/game/index.php?page=messages',
                data=form_data).text
            soup = BeautifulSoup(response, features="html.parser")
            for msg in soup.findAll("li", {"class": 'msg'}):
                if msg["data-msg-id"] not in self.expo_messages:
                    self.expo_messages[msg["data-msg-id"]] = ExpoMessage(self, msg)

        print('All expo messages pushed into database')

    def chk_get_attacked(self):
        """
        :return: True if hostile action detected (includes spy etc.)
        """
        response = self.session.post('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                     'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1'
                                     .format(self.server_number, self.server_language),
                                     headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        if response['hostile'] > 0:
            return True
        else:
            return False

    def chk_get_neutral(self):
        """
        :return: True if neutral action detected
        """
        response = self.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?'
                                    'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1'
                                    .format(self.server_number, self.server_language),
                                    headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        if response['neutral'] > 0:
            return True
        else:
            return False

    def logout(self):
        """
        Ends the session
        :return:
        """
        self.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=logout'
                         .format(self.server_number, self.server_language))

    def read_missions(self):
        """
        sets the self.missions[] array in the format of self.missions[Mission,Mission]
        :return: None
        """
        response = self.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                    'component=movement'
                                    .format(self.server_number, self.server_language)).text
        soup = BeautifulSoup(response, features="html.parser")
        events = soup.find_all("tr", {"class": "eventFleet"})
        self.missions = []
        if events:
            for event in events:
                id = event["id"].replace("eventRow-", "")
                mission_type = int(event["data-mission-type"])
                return_flight = True if event["data-return-flight"] == "true" else False
                arrival_time = int(event["data-arrival-time"])
                to_moon = True if event.find("td", {"class": "destFleet"}).find("figure", {"class": "moon"}) else False
                from_moon = True if event.find("td", {"class": "originFleet"}).find("figure",
                                                                                    {"class": "moon"}) else False
                coords_from_list = event.find("td", {"class": "coordsOrigin"}).find("a").text.strip().replace("[",
                                                                                                              "").replace(
                    "]", "").split(":")
                coords_from = Coordinate(coords_from_list[0], coords_from_list[1], coords_from_list[2],
                                         2 if from_moon else 1)
                coords_to_list = event.find("td", {"class": "destCoords"}).find("a").text.strip().replace("[",
                                                                                                          "").replace(
                    "]", "").split(":")
                coords_to = Coordinate(coords_to_list[0], coords_to_list[1], coords_to_list[2], 2 if to_moon else 1)
                hostile = True if event.find("td", {"class": "countDown"}).find("span", {"class": "hostile"}) else False

                details = BeautifulSoup(event.find("span", {"class": "tooltipRight"}).attrs["title"],
                                        features="html.parser")
                details_rows = details.find_all("td")
                ships = []
                resources = Resources()

                details_rows_clean = [row for row in details_rows if row.text != ' ']

                for i in range(0, int(len(details_rows_clean)), 2):
                    text = details_rows_clean[i].text.replace(":", "")
                    value = details_rows_clean[i + 1].text.replace(".", "")
                    if text in static_lists.ships:
                        ships.append([text, int(value)])
                    elif text in static_lists.resources:
                        if text == "Metall":
                            text = "metal"
                        elif text == "Kristall":
                            text = "crystal"
                        else:
                            text = "deuterium"
                        resources.set_value(int(value), text)

                self.missions.append(
                    Mission(id, mission_type, return_flight, hostile, coords_from, coords_to, arrival_time, resources,
                            ships))

    def chk_logged_in(self):
        """
        :return: Bool
        """
        response = self.session.get(
            'https://s{}-{}.ogame.gameforge.com/game/index.php?page=chat'.format(self.server_number,
                                                                                 self.server_language))
        if response.url == f'https://lobby.ogame.gameforge.com?language={self.server_language}':
            return False
        else:
            return True


class AccountFunctions:

    def __init__(self, acc):
        self.acc = acc
        self.config = self.get_expeditions_config(acc.universe)
        self.possible_fleets, self.possible_expos, self.max_wait_time, self.time_between_expos, self.max_expo_slots = 0, 0, 0, 0, 0
        self.fleet_started, self.expo_user_defined_planet = False, False
        self.expo_user_defined_planet_coordinates = ""

    def set_expo_config(self):
        self.max_wait_time = self.config["config"]["max_wait_time"]
        self.time_between_expos = self.config["config"]["time_between_expos"]
        # max expo slots caps at maximum possible expeditions
        self.max_expo_slots = self.config["config"]["max_expo_slots"] if \
            self.config["config"]["max_expo_slots"] <= self.acc.expo_count[1] else self.acc.expo_count[1]
        self.expo_user_defined_planet = self.config["config"]["planet"]["user_defined_planet"]
        self.expo_user_defined_planet_coordinates = self.config["config"]["planet"]["user_defined_planet_coordinates"]

    def start_expeditions_loop(self):
        self.set_expo_config()
        while True:
            try:
                if not self.acc.chk_logged_in:
                    self.acc.login()
                self.chk_fleet_slots()
                self.acc.init_celestials()
                while self.possible_expos > 0 and self.possible_fleets > 0:
                    celestial = self.get_celestial_to_start_from()
                    self.fleet_started = False
                    while not self.fleet_started:
                        self.send_expedition(celestial)
            # except ConnectionError as e:
            #     print("Connection failed...", e)
            #     sleep(60)
            # except AttributeError as e:
            #     print("Unhandled Error occurred", e)
            #     sleep(60)
            # except AssertionError:
            #     traceback.print_exc()
            #     pass
            except Exception as e:
                traceback.print_exc()
                pass

    def chk_fleet_slots(self):
        """
        checks if a fleet slot for an expedition is available, if not pauses until next returning fleet or expo,
        depending on missing slot type
        :return: Bool
        """
        self.acc.read_in_mission_count()
        self.acc.read_missions()
        self.possible_expos = (self.acc.expo_count[1] - self.acc.expo_count[0])
        self.possible_fleets = (self.acc.fleet_count[1] - self.acc.fleet_count[0])
        if self.acc.expo_count[1] < 1:
            print("No Astro research available yet!")
            quit()

        if self.possible_expos < 1 or self.possible_fleets < 1:
            return_times = []
            if self.possible_fleets < 1:
                relevant_missions = [mission for mission in self.acc.missions
                                     if mission.return_flight]
            else:
                relevant_missions = [mission for mission in self.acc.missions
                                     if mission.mission_type == mission_type_ids.expedition
                                     and mission.return_flight]
            for mission in relevant_missions:
                return_times.append(
                    mission.get_arrival_as_datetime() + datetime.timedelta(0, self.time_between_expos))
            earliest_start = min(dt for dt in return_times)
            earliest_start = min(earliest_start,
                                 datetime.datetime.now() + datetime.timedelta(0, self.max_wait_time))
            print("Pause until", earliest_start)
            pause.until(earliest_start)
            return False
        print("Fleet Slots:", self.possible_fleets, "Expo Slots:", self.possible_expos)
        return True

    def get_celestial_to_start_from(self):
        if self.expo_user_defined_planet:
            coord = self.expo_user_defined_planet_coordinates.replace("-", ":").split(":")
            if len(coord) != 4:
                print("Please adjust Coordinate settings for user_defined_planet_coordinates in Config!")
                quit()
            coord_obj = Coordinate(coord[0], coord[1], coord[2], coord[3])
            celestial = self.acc.get_celestial_by_coord(coord_obj)
            celestials = [celestial]
            celestial.reader.read_in_fleet_by_id()
        else:
            # If not user_defined_planet get celestial with max struct points (determined by settings)
            self.acc.read_in_all_fleets()
            celestials = []
            if self.config["config"]["planet"]["fly_from_moon"]:
                celestials += self.acc.moons
            if self.config["config"]["planet"]["fly_from_planet"]:
                celestials += self.acc.planets

            celestial_points = []
            for i in range(len(celestials)):
                celestial = celestials[i]
                ships = []
                for ship, attr in self.config["config"]["ships"].items():
                    ships.append([celestial.ships[ship], attr])
                celestial_points.append([celestial, sum(ship[1]["point_weight"] * ship[0].count for ship in ships)])

            celestial_points_sorted = sorted(celestial_points, key=lambda x: (x[1], x[1]), reverse=True)
            celestial = celestial_points_sorted[[0][0]]

        if self.config["config"]["print_ships_on_planet"]:
            for celestial in celestials:
                print("--------", celestial.name, "--------")
                for ship in celestial.ships:
                    if celestial.ships[ship].count:
                        print("{:.<22}".format(celestial.ships[ship].name) + " -> amount: " + '{: >10}'.format(
                            celestial.ships[ship].count))
        return celestial

    def send_expedition(self, celestial):
        min_over_threshold = self.config["config"]["min_over_threshold"]
        ships = []
        ships_send = []
        for ship, attr in self.config["config"]["ships"].items():
            ships.append([celestial.ships[ship], attr])

        for ship in ships:
            expo_factor = ship[1]["expo_factor"]
            count_available = ship[0].count
            count_max = ship[1]["max"]
            count_min = ship[1]["min"]
            threshold = min(ship[1]["threshold"], count_available)

            count_calc = int((count_available - threshold) / (expo_factor * self.possible_expos))

            if count_calc >= count_max:
                count_send = count_max
            elif count_calc <= count_min:
                count_send = min(count_min, count_available)
            else:
                count_send = count_calc
            if count_send > 0:
                ships_send.append([ship[0], int(count_send)])

        random_system = random.randint(celestial.coordinates.system - self.config["config"]["system_variance"],
                                       celestial.coordinates.system + self.config["config"]["system_variance"])

        if ships_send:
            response = celestial.send_fleet(mission_type_ids.expedition,
                                            Coordinate(celestial.coordinates.galaxy, random_system, 16), ships_send,
                                            resources=[0, 0, 0], speed=10,
                                            holdingtime=1)
        else:  # No ships available for expo
            raise NoShipsAvailableError(celestial)

        if not response[0]:
            raise AttributeError
            # todo: implement custom Errorhandling

        if response[0]:
            self.possible_expos -= 1
            self.possible_fleets -= 1
            self.fleet_started = True

    @staticmethod
    def get_expeditions_config(uni):
        with open(path.abspath("../Config/Expeditions_Config.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d[uni]

    def chk_for_expo_trash(self):
        """
        Check if in any system where own celestials are initialized has debris on position 16
        :return: Coordinate[ ]
        """
        if not self.acc.planets or not self.acc.moons:
            print("Read in Celestials beforehand! Coords needed to identify relevant systems")
            quit()
        expo_debris = []
        systems = []
        for planet in self.acc.planets:
            systems.append(str(planet.coordinates.galaxy) + ":" + str(planet.coordinates.system))
        systems_expo_unique = [Coordinate(coord.split(":")[0],
                                          coord.split(":")[1], 16) for coord in set(systems)]
        for coord in systems_expo_unique:
            debris = self.get_debris_for_galaxy_system(coord.galaxy, coord.system)
            for debris_coord in debris:
                if debris_coord[0].position == 16:
                    expo_debris.append(debris_coord)
        return expo_debris

    def get_debris_for_galaxy_system(self, galaxy, system):
        """
        Get list of Debris in System
        :param galaxy: int
        :param system: int
        :return: Debris_in_System[[Coordinate, Resources, int Recyclers/Pathfinders], ]
        """
        form_data = {'galaxy': galaxy,
                     'system': system}
        response = self.acc.session.post(
            f'https://s{self.acc.server_number}-{self.acc.server_language}.ogame.gameforge.com/game/index.php?page=ingame&component=galaxyContent&ajax=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}, data=form_data).json()
        soup = BeautifulSoup(response["galaxy"], features="html.parser")
        debris_raw = [debris.text.strip() for debris in soup.find_all("tr", {"class": "expeditionDebrisSlot"}) if
                      debris.text.strip() != '']
        debris_raw += [debris.text.strip() for debris in soup.find_all("td", {"class": "debris"}) if
                       debris.text.strip() != '']
        debris_list = []
        if debris_raw:
            for debris in debris_raw:
                # Coordinates
                coord_raw = re.search("\[\d+:\d+:\d+\]", debris).group(0)
                coord_cleaned = coord_raw.replace("[", "").replace("]", "").split(":")
                coord = Coordinate(coord_cleaned[0], coord_cleaned[1], coord_cleaned[2], 3)
                # Resources
                debris_metal = re.search("\d+", debris.replace(".", "").split("Metall")[1]).group(0)
                debris_crystal = re.search("\d+", debris.replace(".", "").split("Kristall")[1]).group(0)
                resources = Resources(debris_metal, debris_crystal, 0)
                # Needed Ships to Recycle
                ships_raw = re.search("Benötigte.*: \d+", debris).group(0).replace(".",
                                                                                   "")  # todo: Adjust to match delimiter 1.000 etc.
                ships = int(re.search("\d+", ships_raw).group(0))

                debris_list.append([coord, resources, ships])
        return debris_list


if __name__ == "__main__":
    a1 = Account(universe="Pasiphae", username="strabbit@web.de", password="OGame!4myself")
    a1.init_celestials()
    a1.AccountFunctions.chk_for_expo_trash()
    # a1.AccountFunctions.chk_for_expo_trash()
    # a1.AccountFunctions.get_expo_trash()
    #
    # a1.get_expo_messages()
    # # """
    # for message in a1.expo_messages:
    #     a1.expo_messages[message].delete_message()
    # # """
    print("Done...")
