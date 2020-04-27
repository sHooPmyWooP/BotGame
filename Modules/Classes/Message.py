import re
import sqlite3
import os
from datetime import datetime

try:
    from Modules.Resources.Static_Information.Constants import expo_messages, resources
except ModuleNotFoundError:
    from Resources.Static_Information.Constants import expo_messages, resources

from .Coordinate import Coordinate
from .Resources import Resources


class Message:
    """
    represents one message from Inbox
    """

    def __init__(self, acc, msg):
        self.acc = acc
        self.id = int(msg["data-msg-id"])
        self.timestamp = convert_timestamp(
            msg.find("span", {"class": "msg_date"}).text)  # datetime of recieving the message
        self.msg_from = msg.find("span", {"class": "msg_sender"}).text  # Name of Player/Computer that sent the msg

    def delete_message(self):
        """deletes the message from the inbox"""

        if isinstance(self, ExpoMessage):
            if self.result_type == "unclassified":
                print(f"Not deleting Message {self.id} because result_type is unclassified. "
                      f"Please adjust Classification and rerun.")
                return False

        form_data = {
            "messageId": self.id,
            "action": 103,
            "ajax": 1
        }
        delete = self.acc.session.post(
            f'https://s{self.acc.server_number}-{self.acc.server_language}.ogame.gameforge.com/game/index.php?page=messages',
            data=form_data)

    @staticmethod
    def chk_regex_case_insensitive(content, search_string):
        if re.search(search_string, content, re.IGNORECASE):
            return True
        else:
            return False


class SpyMessage(Message):
    def __init__(self, acc, msg):
        super().__init__(acc, msg)
        # we've been spied on - details probably not interesting
        if self.msg_from == "Raumüberwachung":
            return

        self.target_coords = Coordinate()
        self.target_player_name = ""  # todo: Maybe not that important after all. Possibly get from Universe-API-DB with coords
        self.resources = Resources()
        self.api_key = ""

        msg_title = msg.find("span", {"class": "msg_title"})
        msg_actions = msg.find("span", {"class": "msg_actions"})

        #  Coords
        coords = re.search("\[\d+:\d+:\d+\]", msg_title.find("a").text).group(0)
        coord = coords.split(":")
        target_coords = [0, 0, 0]
        for i, x in enumerate(coord):
            target_coords[i] = x.replace("[", "").replace("]", "")
        self.target_coords = Coordinate(target_coords[0], target_coords[1], target_coords[2])

        #  Resources
        resspan = msg.findAll("span", {"class": "resspan"})
        res_list = ['Metall', 'Kristall', 'Deuterium']  # todo: translate
        resources = []
        amount = 0
        for res in resspan:
            for res_name in res_list:
                result = re.search(f'{res_name}: \d+.?\d*', res.text)
                try:
                    resources.append([result.group(0), res_name])
                except AttributeError:
                    pass
        for findings in resources:
            # get Type of Resource
            if findings[1] == "Metall":
                type = "metal"
            elif findings[1] == "Kristall":
                type = "crystal"
            elif findings[1] == "Deuterium":
                type = "deuterium"
            # get amount of Resource
            for s in findings[0].split():
                try:
                    amount = int(s.replace(".", ""))  # remove delimiter todo: check for millions etc.
                except ValueError as e:
                    pass
            self.resources.set_value(amount, type)

        # API Key
        html_api = msg.find("span", {"class": "icon_apikey"})
        match_string = r"value='(.*)'"
        api_key_regex_object = re.search(match_string, str(html_api)).group(0)
        api_key = api_key_regex_object.split("value='")[1]
        api_key = api_key.split("'")[0]
        self.api_key = api_key

        self.push_spy_message_to_db()

    def push_spy_message_to_db(self):
        conn = sqlite3.connect('Resources/db/messages.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS SPY_MESSAGES(
        id integer primary key,
        spy_timestmap text,
        msg_from text,
        target_coords text,
        resources text,
        api_key text);
        """)

        statement = "INSERT OR REPLACE INTO 'SPY_MESSAGES' VALUES (?, ?, ?,?, ?, ?);"
        tuple = (
            self.id, self.timestamp, self.msg_from, self.target_coords.get_coord_str(),
            self.resources.get_resources_str(),
            self.api_key)
        c.execute(statement, tuple)
        conn.commit()
        conn.close()


class ExpoMessage(Message):
    def __init__(self, acc, msg):
        super().__init__(acc, msg)
        self.content = msg.find("span", {"class": "msg_content"}).text.strip()

        self.result_type = self.classify_result()
        self.push_expo_message_to_db()

    def push_expo_message_to_db(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        database = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)), 'Resources', 'db', 'messages.db')
        conn = sqlite3.connect(database)
        c = conn.cursor()

        self.push_table_expo_message(conn, c)

        if self.result_type:
            self.get_result_details_amount(conn, c)

        conn.close()

    def classify_result(self):
        for key in expo_messages.keywords.keys():
            for keyword in expo_messages.keywords[key]:
                if self.chk_regex_case_insensitive(self.content, keyword):
                    return key
        return "unclassified"

    def get_result_details_amount(self, conn, c):
        if self.result_type in ["nothing", "delay", "pirats", "aliens", "delayed_return", "faster_return", "fleet_loss"]:
            self.push_table_expo_message_details(conn, c, self.result_type, 1)
        elif self.result_type == "resources":
            for res in [resources.metall, resources.kristall, resources.deuterium]:
                pattern = re.compile(res + ' (\d*\.)*\d+')
                if pattern.search(self.content):
                    self.push_table_expo_message_details(conn, c, res, re.search('(\d*\.)*\d+', self.content)
                                                         .group(0).replace(".", ""))
        elif self.result_type == "ships":
            ships = re.split(': \d+', self.content.split("sich der Flotte an:")[1])[:-1]
            amount = [i for i in re.findall('(\d+\.?)+\d?', self.content)]
            for i, ship in enumerate(ships):
                self.push_table_expo_message_details(conn, c, ship, amount[i])

        elif self.result_type == 'dark_matter':
            pattern = re.compile('Dunkle Materie' + ' (\d*\.)*\d+')
            if pattern.search(self.content):
                self.push_table_expo_message_details(conn, c, 'Dunkle Materie', re.search('(\d*\.)*\d+', self.content)
                                                     .group(0).replace(".", ""))
        elif self.result_type == 'item':
            item = ''.join(self.content.split(' wurde dem Inventar hinzugefügt')[0].split('.Ein ')[1])
            self.push_table_expo_message_details(conn, c, item, 1)
        else:
            print(f'expo message with id {self.id} cannot pushed into details database. Result_type not found')

    def push_table_expo_message(self, conn, c):
        c.execute("""
                CREATE TABLE IF NOT EXISTS EXPO_MESSAGES(
                id integer primary key,
                expo_timestamp datetime,
                msg_from text,
                content text,
                result_type text, 
                universe text);
                """)

        statement = "INSERT OR REPLACE INTO 'EXPO_MESSAGES' VALUES (?, ?, ?, ?, ?, ?);"
        tuple = (self.id, self.timestamp, self.msg_from, self.content, self.result_type, self.acc.server_name)
        c.execute(statement, tuple)
        # print(tuple)
        conn.commit()

    def push_table_expo_message_details(self, conn, c, details, amount):
        c.execute("""
            CREATE TABLE IF NOT EXISTS EXPO_MESSAGES_DETAILS(
                    id integer not null,
                    universe text,
                    expo_timestamp datetime,
                    content text,
                    result_type text,
                    result_details text not null,
                    result_amount int,
                    PRIMARY KEY (id, result_details)
                    );
        """)
        statement = "INSERT OR REPLACE INTO 'EXPO_MESSAGES_DETAILS' VALUES (?, ?, ?, ?, ?, ?, ?);"
        tuple = (
            self.id, self.acc.server_name, self.timestamp, self.content, self.result_type, details, amount)
        c.execute(statement, tuple)
        conn.commit()


class CombatReport(Message):
    def __init__(self, acc, msg, push_into_db=True, min_units_to_push=1000000):
        super().__init__(acc, msg)
        self.json_data = self.get_json_from_cr(acc.session.get(
            acc.get_http_string() + f'page=standalone&component=displayMessageNewPage&messageId={self.id}&tabid=21&ajax=1').text)
        print(json.dumps(self.json_data))
        if self.json_data['isExpedition']:
            self.expo_msg_id = (self.id + 1)

            # Attacker
            __attacker_json = self.json_data['attackerJSON']['member'][0]
            self.attacker_name = __attacker_json['ownerName']
            self.attacker_coordinate = Coordinate.create_from_string(__attacker_json['ownerCoordinates'])

            # Defender
            __defender_json = self.json_data['defenderJSON']['member']
            __defender_json = __defender_json[[x for x in __defender_json][0]]
            self.defender_class = __defender_json['ownerCharacterClassName']
            self.defender_coordinates = Coordinate.create_from_string(__defender_json['ownerCoordinates'])
            self.defender_ships_before_combat = self.get_start_ships()
            self.defender_lost_ships = self.json_data['defenderJSON']['combatRounds'][-1]['losses']
            self.debris_metal = self.json_data['debris']['metalTotal']
            self.debris_crystal = self.json_data['debris']['crystalTotal']
            s = json.dumps(self.json_data)

            if push_into_db and (self.json_data['statistic']['lostUnitsAttacker'] + self.json_data['statistic'][
                'lostUnitsDefender']) > min_units_to_push:
                dir_path = os.path.dirname(os.path.abspath(__file__))
                database = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)), 'Resources', 'db',
                                        'messages.db')
                conn = sqlite3.connect(database)
                c = conn.cursor()
                self.push_into_db(conn, c)
        else:
            return



    def list_or_dict(self, data=None):
        return 0 if self.__attacker_is_ai else self.__attacker_id #data[[x for x in data]][0]

    def get_json_from_cr(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')

        scripts = soup.find_all('script')
        for script in scripts:
            if 'jQuery.parseJSON' in script.text:
                jsonStr = script.text.strip()
                jsonStr = jsonStr.split(';')[0].split('\'')[1]
                return json.loads(jsonStr)
        return None

    def get_start_ships(self):
        ships = {}
        ships_json = self.json_data['defender'][[x for x in self.json_data['defender']][0]]['shipDetails']
        for ship_id in ships_json:
            ships[ship_id] = ships_json[ship_id]['count']

        return ships

    def push_into_db(self, conn, c):
        c.execute("""
            CREATE TABLE IF NOT EXISTS COMBAT_REPORTS(
                    id integer NOT NULL PRIMARY KEY,
                    universe text,
                    expo_timestamp datetime,
                    json text,
                    expo_id INTEGER,
                    ships_lost_json text
                    );
        """)
        statement = "INSERT OR REPLACE INTO 'COMBAT_REPORTS' VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        # combat report from expo is always one id before expo_message id
        tuple = (self.id, self.acc.server_name, self.timestamp, json.dumps(self.json_data), self.expo_msg_id, json.dumps(self.defender_lost_ships),
                 self.debris_metal, self.debris_crystal)
        c.execute(statement, tuple)
        conn.commit()

    def get_attacker_id(self, datas):
        if type(datas) == list:
            return datas[0]['ownerID']
        elif type(datas) == dict:
            return datas[[x for x in datas][0]]['ownerID']


def convert_timestamp(s):
    d = s.split(' ')[0].split('.')
    t = s.split(' ')[1].split(':')

    return datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))
