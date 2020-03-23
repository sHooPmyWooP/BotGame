from Classes.Coordinate import Coordinate, Destination


class Moon:
    def __init__(self, id, planet, jumpgate):
        self.id = id
        self.planet = planet
        self.jumpgate = jumpgate
        self.coords = Coordinate(planet.coordinates.galaxy, planet.coordinates.system, planet.coordinates.position,
                                 Destination.Moon)

    def read_fleet(self, read_moon=False):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=shipyard&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        for ship in soup.find_all("li", {"class": "technology"}):
            try:
                count = int(ship.text)
            except ValueError:  # Ships currently build - refer to currently accessible amount
                count = ship.text.split("\n")[-1].strip()  # get last element of list
            self.planet.ships[ship['aria-label']] = Ship(ship['aria-label'], ship['data-technology'],
                                                         count, self)
