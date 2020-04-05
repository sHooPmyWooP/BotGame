import sys
from json import load
from os import path

import requests

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi


class TelegramBot:
    def __init__(self):
        self.config = self.get_config()
        self.TOKEN = self.config["Token"]
        self.CHAT_ID = self.config["ChatID"]
        self.URL = "https://api.telegram.org/bot{}".format(self.TOKEN)

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def send_message(self, text):
        url = self.URL + "/sendMessage?text={}&chat_id={}".format(text, self.CHAT_ID)
        self.get_url(url)

    @staticmethod
    def get_config():
        with open('Config/Telegram_Config.json', encoding="utf-8") as f:
            conf = load(f)
        return conf
