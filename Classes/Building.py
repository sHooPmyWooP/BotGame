class Building:

    def __init__(self, name, id, level, building_type, planet, is_possible, in_construction):
        self.name = name
        self.id = id
        self.level = int(level)
        self.type = building_type
        self.planet = planet
        self.is_possible = is_possible
        self.in_construction = in_construction

    def get_name(self):
        return self.name

    def upgrade(self):
        """
        upgrade building
        todo: not working by now
        :return: True on success
        """
        print("Upgrade done...")
        return True
