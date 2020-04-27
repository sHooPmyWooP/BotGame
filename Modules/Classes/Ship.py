import os
from Modules.Classes.Resources import Resources
from Modules.Classes.Research import Research

# ships read in in Account.readIn

class Ship:

    def __init__(self, name, id, count, planet):
        self.name = name
        self.id = id
        if isinstance(count, str):
            self.count = int(count.replace(".", ""))
        else:
            self.count = count
        self.planet = planet

        static_infos = self.get_infos()
        self.costs = Resources(0, 0, 0)
        self.cargo = ""
        self.speed = ""

    def __repr__(self):
        return self.name + " count: " + str(self.count)

    def get_name_by_id(self, id):
        if self.id == id:
            return self.name

    def build(self):
        """todo: add"""
        pass

    def cargo(self, hyper_tech):
        pass


    def read_infos(self, name, research):
        with open(os.path.abspath('../Resources/Static_Information/Building_Base_Info'), 'r') as file:
            for line in file:
                ship = line.split('|')
                if ship[0] == name:
                    self.costs = Resources(ship[1], ship[2], ship[3])
                    self.cargo = ship[7] * (1 + research * 0.05)
                    self.speed =0
            return Exception


    @staticmethod
    def calc_cargo(ships, hyper_tech):
        cargo = 0
        for ship in ships:
            cargo += ship.cargo
        return cargo
