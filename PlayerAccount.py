class PlayerAccount:
    def __init__(self, universe, json_uni):
        self.uni_number = json_uni["server"]["number"]
        self.player_name = json_uni["name"]
        self.universe = universe
        self.fleet_slots = 0
        self.is_active = False
        self.officer = [] # todo: naming anpassen (?) - eventuell nicht als liste

    def send_fleet(self,fleet,coordinate,mission_id):
        """
        todo: implement
        send fleet to attack or spy on target
        :param fleet: Fleet object
        :param coordinate:  Coordinate object
        :param mission_id: Mission ID (either Attack, Spy or Transport)
        :return: True on success
        """
        pass

    def start_farming(self, requirement_target, coordinate_range, planet_self):
        """
        todo: implement
        Start Scanner Class Object
        :param requirement_target: mines, ressource, capacity...?
        :param coordinate_range: [ ] Coordinates to Scan
        :param planet_self: Planet
        :return: ?
        """
        pass

    def get_messages(self):
        """
        check for new in-game Messages
        :return: Message
        """
