import datetime
import json
import sys
from time import sleep

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
            botConfig = open('Config/Telegram_Config.json', encoding="utf-8")  # check
            self.telegramBot = TelegramBot()
        except:
            self.telegramBot = None
        self.attack_missions = {}

    def safety_module(self):
        while True:
            try:
                self.acc.login()
                if self.acc.chk_get_attacked():
                    self.acc.read_in_all_celestial_basics()
                    self.acc.read_missions()
                    target_coords = []
                    targeted_celestials = []
                    for mission in self.acc.missions:
                        if mission.hostile:
                            if mission.mission_type == mission_type_ids.attack:
                                if mission.id not in self.attack_missions.keys():
                                    self.attack_missions[mission.id] = mission
                                    target_coords.append(mission.coord_to)
                                    for coord in target_coords:
                                        for celestial in self.acc.planets + self.acc.moons:
                                            if str(celestial.coordinates) == str(coord):
                                                self.attack_missions[mission.id].attack_target = celestial
                                                if self.telegramBot:
                                                    self.telegramBot.send_message(
                                                        str(celestial.coordinates) +
                                                        " is beeing attacked at " +
                                                        mission.get_arrival_as_string())
                    # for celestial in targeted_celestials:
                    #     celestial.reader.read_defenses()
                    #     celestial.build_defense_by_ratio()
                    #     celestial.build_defense_routine(1000)
                    sleep(self.waiting_time)
                else:
                    sleep_until = datetime.datetime.now() + datetime.timedelta(0, self.waiting_time)
                    print("No Attacks, sleep until:", sleep_until)
                    sleep(self.waiting_time)
            except Exception as e:
                self.telegramBot.send_message(
                    "Exception! Sleeping 60 Seconds before retry.\n Exception:" + str(e))
                print("Exception! Sleeping 60 Seconds before retry.", e)
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
