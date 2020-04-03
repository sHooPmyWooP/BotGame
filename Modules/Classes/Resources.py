class Resources():
    def __init__(self, metal=0, crystal=0, deut=0):
        self.metal = metal
        self.crystal = crystal
        self.deuterium = deut

    def __repr__(self):
        return str([self.metal, self.crystal, self.deuterium])

    def get_metal(self):
        return self.metal

    def get_crystal(self):
        return self.crystal

    def get_deut(self):
        return self.deut

    def set_metal(self, x):
        self.metal = x

    def set_crystal(self, x):
        self.crystal = x

    def set_deuterium(self, x):
        self.deuterium = x

    def set_value(self, x, resource):
        if resource == "metal":
            self.metal = x
        if resource == "crystal":
            self.crystal = x
        if resource == "deuterium":
            self.deuterium = x
        else:
            pass

    def get_resources_str(self):
        return f"{self.metal}:{self.crystal}:{self.deuterium}"
