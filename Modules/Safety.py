import datetime
import json
import sys
from os import path
from time import sleep

sys.path.append(
    path.dirname(path.dirname(path.abspath(__file__))))  # necessary to make the file structure work on raspi

from Modules.Classes.Account import Account
from Modules.Classes.TelegramBot import TelegramBot

try:
    from Modules.Resources.Static_Information.Constants import mission_type_ids
except ModuleNotFoundError:
    from Resources.Static_Information.Constants import mission_type_ids


class Safety():
    def __init__(self, uni):
        self.config = self.get_config(uni)
        self.acc = Account(uni, self.config["username"], self.config["password"])
        self.waiting_time = self.config["config"]["waiting_time"]
        try:
            bot_config = open('Config/Telegram_Config.json', encoding="utf-8")  # check
            self.telegramBot = TelegramBot()
        except:
            self.telegramBot = None
        self.handeld_attacks = {}

    def safety_module(self):
        while True:
            try:
                self.acc.login()
                if self.acc.chk_get_attacked():
                    self.acc.init_celestials()
                    self.acc.read_missions()
                    target_coords = []
                    # GETTING THE MISSION
                    for mission in self.acc.missions:
                        target_coords = []
                        if mission.hostile:
                            if mission.mission_type == mission_type_ids.attack:
                                if mission.id not in self.handeld_attacks.keys():
                                    self.handeld_attacks[mission.id] = mission
                                    target_coords.append(mission.coord_to)
                                    # GETTING THE TARGET
                                    for coord in target_coords:
                                        for celestial in self.acc.planets + self.acc.moons:
                                            if str(celestial.coordinates) == str(coord):
                                                self.handeld_attacks[mission.id].attack_target = celestial
                                                message = str(
                                                    celestial.coordinates) + " " + celestial.name + " is beeing attacked at " + mission.get_arrival_as_string()
                                                print(message)
                                                if self.telegramBot:
                                                    self.telegramBot.send_message(message)
                                                break
                    # for celestial in targeted_celestials:
                    #     celestial.reader.read_defenses()
                    #     celestial.build_defense_by_ratio()
                    #     celestial.build_defense_routine(1000)
                    sleep_until = datetime.datetime.now() + datetime.timedelta(0, self.waiting_time)
                    print("Sleep until next check:", sleep_until)
                    sleep(self.waiting_time)
                else:
                    sleep_until = datetime.datetime.now() + datetime.timedelta(0, self.waiting_time)
                    message = "No Attacks, sleep until: " + str(sleep_until)
                    print(message)
                    # if self.telegramBot:
                    #     self.telegramBot.send_message(message)
                    sleep(self.waiting_time)
            except Exception as e:
                message = f"Exception! Sleeping {self.waiting_time} Seconds before retry.\n Exception:" + str(e)
                self.telegramBot.send_message(message)
                print(message)
                sleep(self.waiting_time)

    @staticmethod
    def get_config(uni):
        with open('Config/Safety_Config.json', encoding="utf-8") as f:
            d = json.load(f)
        return d[uni]


if __name__ == "__main__":
    universe = sys.argv[1]
    s = Safety(universe)
    s.safety_module()
