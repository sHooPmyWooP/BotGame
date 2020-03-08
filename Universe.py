import json
import requests
import jsonpickle
from PlayerAccount import PlayerAccount
from serverAPI import server_api

language = "de"  # todo: move to config or make dynamic


class Universe:
    def __init__(self, acc, json_uni):
        self.acc = acc
        self.json_uni = json_uni
        self.player_account = PlayerAccount(self)
        self.settings = {}
        try:
            #in der Firma gehen keine requests, daher auskommentiert und response lokal abgelegt
            server_api_request = requests.get("https://lobby.ogame.gameforge.com/api/servers")
            server_api_json = server_api_request.json()
        except Exception:#requests.exceptions.ConnectionError: #uncomment when testing is done
            print("Server API Request didn't load. Using local file.")
            server_api_json = json.loads(server_api)
        for server in server_api_json:
            if self.player_account.uni_number == server["number"]:
                self.name = server["name"]
                self.language = server["language"]
                for key in server["settings"]:
                    self.settings[key] = server["settings"][key]
        # print("Created Universe:", jsonpickle.encode(self))


if __name__ == "__main__":
    pass
    # u1 = Universe(json_acc)
