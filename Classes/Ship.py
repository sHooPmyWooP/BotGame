class Ship:

    def __init__(self, name, id, count, planet):
        self.name = name
        self.id = id
        if isinstance(count, str):
            self.count = int(count.replace(".", ""))
        else:
            self.count = count
        self.planet = planet

    def get_name_by_id(self, id):
        if self.id == id:
            return self.name

    def build(self):
        """todo: add"""
        pass
