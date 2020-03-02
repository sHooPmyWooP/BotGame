import json
import requests

language = "de" # todo: move to config or make dynamic

class Universe:
    def __init__(self, json_uni):
        self.json_uni = json_uni
        self.uni_number = json_uni["server"]["number"]
        self.player_name = json_uni["name"]
        self.settings = {}
        server_api_request = requests.get("https://lobby.ogame.gameforge.com/api/servers")
        server_api_json = server_api_request.json()
        for server in server_api_json:
            if self.uni_number == server["number"]:
                self.name = server["name"]
                self.language = server["language"]
                for key in server["settings"]:
                    self.settings[key] = server["settings"][key]

if __name__ == "__main__":
    u1 = Universe(json_acc)
