class Building:

    def __init__(self, name, wfid, level, building_type, planet):
        self.name = name
        self.id = wfid
        self.level = level
        self.type = building_type
        self.planet = planet

    def upgrade(self):
        """
        upgrade building
        :return: True if successful
        """
        self.level += 1
        return True
