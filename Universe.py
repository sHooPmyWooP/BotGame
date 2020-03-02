import json

class Universe:
    def __init__(self, json_uni):
        self.json_uni = json_uni
        pass

if __name__ == "__main__":
    json_acc = str({'server': {'language': 'de', 'number': 167}, 'id': 107550, 'gameAccountId': 107550, 'name': 'Mogul Spacewalk', 'lastPlayed': '2020-03-02T13:22:29+0100', 'lastLogin': '2020-03-02T12:22:29+0000', 'blocked': False, 'bannedUntil': None, 'bannedReason': None, 'details': [{'type': 'literal', 'title': 'myAccounts.rank', 'value': '2709'}, {'type': 'localized', 'title': 'myAccounts.status', 'value': 'playerStatus.active'}], 'sitting': {'shared': False, 'endTime': None, 'cooldownTime': None}, 'trading': {'trading': False, 'cooldownTime': None}})
    u1 = Universe(json_acc)