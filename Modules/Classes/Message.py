import re
import sqlite3

from .Coordinate import Coordinate
from .Resources import Resources


class Message:
    """
    represents one message from Inbox
    """
    def __init__(self, acc, msg):
        self.acc = acc
        self.id = msg["data-msg-id"]
        self.timestamp = msg.find("span", {"class": "msg_date"}).text  # datetime of recieving the message
        self.msg_from = msg.find("span", {"class": "msg_sender"}).text  # Name of Player/Computer that sent the msg

    def delete_message(self):
        """deletes the message from the inbox"""
        form_data = {
            "messageId": self.id,
            "action": 103,
            "ajax": 1
        }
        delete = self.acc.session.post(
            f'https://s{self.acc.server_number}-{self.acc.server_language}.ogame.gameforge.com/game/index.php?page=messages',
            data=form_data)


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
        self.delete_message()

    def push_spy_message_to_db(self):
        conn = sqlite3.connect('Resources\db\spy_messages.db')
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

        if re.search("erbeutet", self.content).group(0):
            self.type = "resources"

        self.push_expo_message_to_db()
        self.delete_message()

    def push_expo_message_to_db(self):
        conn = sqlite3.connect('../Resources/db/messages.db')
        # conn = sqlite3.connect('Resources\db\expo_messages.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS EXPO_MESSAGES(
        id integer primary key,
        expo_timestamp text,
        msg_from text,
        content text
        result text);
        """)

        statement = "INSERT OR REPLACE INTO 'EXPO_MESSAGES' VALUES (?, ?, ?, ?);"
        tuple = (self.id, self.timestamp, self.msg_from, self.content)
        c.execute(statement, tuple)
        conn.commit()
        conn.close()
