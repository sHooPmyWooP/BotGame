import re

from Classes.Resources import Resources


class Message:
    """
    represents one message from Inbox
    """

    def __init__(self, msg):
        self.id = msg["data-msg-id"]
        self.timestamp = msg.find("span", {"class": "msg_date"}).text  # datetime of recieving the message
        self.msg_from = msg.find("span", {"class": "msg_sender"}).text  # Name of Player/Computer that sent the msg


class SpyMessage(Message):
    def __init__(self, msg):
        super().__init__(msg)
        # we've been spied on - details probably not interesting
        if self.msg_from == "Raumüberwachung":
            return

        self.target_coords = [0, 0, 0]
        self.target_player_name = ""
        self.resources = Resources()
        self.api_key = ""

        title = msg.find("span", {"class": "msg_title"})

        coords = re.search("\[\d+:\d+:\d+\]", title.find("a").text).group(0)

        for coord in coords:
            coord = coord.split(":")
            for i, x in enumerate(coord):
                self.target_coords[i] = x.replace("[", "").replace("]", "")

        print(self.msg_from, self.timestamp, self.id, self.target_coords)
