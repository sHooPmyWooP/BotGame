class Building:

    def __init__(self, name, id, level, planet):
        self.name = name
        self.id = id
        self.level = level
        self.planet = planet

    def upgrade(self):
        """
        upgrade building
        :return: True if successful
        """
        self.level += 1
        return True
