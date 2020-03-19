import re

from bs4 import BeautifulSoup


class Defense:

    def __init__(self, name, id, count, planet):
        """
        :param name:
        :param wfid:
        :param count:
        :param planet:
        """
        self.name = name
        self.id = id
        self.count = count
        self.planet = planet
        self.max_build = 0

    def build(self, amount=1):
        """
        Upgrade Building to next level
        :param amount: int (default 1)
        :return: None
        """
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=defenses&cp={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id)).text
        self.get_init_build_token(response)

        build_url = 'https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&' \
                    'component=defenses&modus=1&token={}&type={}&menge={}' \
            .format(self.planet.acc.server_number, self.planet.acc.server_language,
                    self.planet.acc.build_token, self.id, amount)
        response = self.planet.acc.session.get(build_url)
        print(str(amount) + " " + self.name + " built on " + self.planet.name)

    def read_max_build(self):
        response = self.planet.acc.session.get('https://s{}-{}.ogame.gameforge.com/game/index.php?page=ingame&'
                                               'component=technologydetails&cp={}&action=getDetails&technology={}'
                                               .format(self.planet.acc.server_number, self.planet.acc.server_language,
                                                       self.planet.id, self.id)).text
        soup = BeautifulSoup(response, features="html.parser")
        self.max_build = int(soup.find("input", {"name": "build_amount"})["max"])
        return self.max_build

    def get_init_build_token(self, content):
        """
        necessary to process build method
        :param content: str (response)
        :param component: str (supply/facility)
        :return:
        """
        marker_string = 'component=defenses&modus=1&token='
        for re_obj in re.finditer(marker_string, content):
            self.planet.acc.build_token = content[re_obj.start() + len(marker_string): re_obj.end() + 32]
