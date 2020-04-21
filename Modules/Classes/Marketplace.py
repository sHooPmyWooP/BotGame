import re


class Marketplace:
    def __init__(self, acc):
        self.acc = acc
        self.selling = []  # Angebote
        self.buying = []  # Gesuche

    def get_max_page(self, type="BuyingItems"):
        response = self.acc.session.get(url=self.acc.index_php + '?page=ingame&component=marketplace&tab=buying&action'
                                                                 f'=fetch{type}&ajax=1&pagination%5Bpage%5D=1',
                                        headers={'X-Requested-With': 'XMLHttpRequest'}).text
        max_pages = int(re.search("\d+", response.split("numPages\\")[1].replace(":", "").replace(".", "")).group(
            0))  # numPages marks the number of total pages
        return max_pages
