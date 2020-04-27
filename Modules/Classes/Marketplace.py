import re
from random import randint
from time import sleep

from bs4 import BeautifulSoup


class Marketplace:
    def __init__(self, acc):
        self.acc = acc
        self.selling = []  # Angebote
        self.buying = []  # Gesuche

    def get_max_page(self, action):
        # todo: check if buying is correct here in any case (url)
        response = self.acc.session.get(
            url=self.acc.index_php + f'?page=ingame&component=marketplace&tab={action.lower()}&action'
                                     f'=fetch{action.title()}Items&ajax=1&pagination%5Bpage%5D=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}).text
        max_pages = int(re.search("\d+", response.split("numPages\\")[1].replace(":", "").replace(".", "")).group(
            0))  # numPages marks the number of total pages
        return max_pages

    def get_offers_by_action(self, action):
        """
        :param action: str // either "buying" or "selling"
        """
        max_page = 1  # self.get_max_page(action)
        print(f"Reading {max_page} pages for {action} Offers")
        for page in range(1, max_page + 1):
            page
            response = self.acc.session.get(
                url=self.acc.index_php + f'?page=ingame&component=marketplace&tab={action.lower()}&action'
                                         f'=fetch{action.title()}Items&ajax=1&pagination%5Bpage%5D={page}',
                headers={'X-Requested-With': 'XMLHttpRequest'}).json()
            soup = BeautifulSoup(response["content"]['marketplace/marketplace_items_buying'], features="html.parser")
            rows = soup.find_all("div", {"class": "row"})

            for row in rows:
                if action == "buying":
                    self.buying.append(Buying(row))
                elif action == "selling":
                    self.selling.append(Selling(row))
            print(f"Done with page {page}/{max_page}")
            sleep(randint(10, 100) / 100)  # don't be too obvious here

        for offer in self.buying:
            print(offer)

        print("Done...")


class Buying:
    def __init__(self, html):
        # ID
        self.id = html.find("a").attrs["data-itemid"]
        self.type = ""

        # Type
        try:
            classes = html.find("div", {"class": "thumbnail"}).find("div").attrs["class"]
        except AttributeError:
            self.type = "item"

        if not self.type:
            if "resource" in classes:
                self.type = "resource"
            elif "ship" in classes:
                self.type = "ship"

        self.resource_type = html.find("h3").text
        self.resource_quantity = int(html.find("div", {"class": "quantity"}).text.replace(".", ""))

        price = html.find("div", {"class": "price"})
        self.price_type = price.find("h3").text
        self.price_quantity = int(price.find("div", {"class": "quantity"}).text.replace(".", ""))
        self.price_ratio = round(self.price_quantity / self.resource_quantity, 2)

    def __str__(self):
        return f"ID: {self.id}\t Offer: {self.resource_type:.<22}\tQuantity: {self.resource_quantity:.>15}\tPrice: {self.price_type:>9} - {self.price_quantity:>12}\tRatio: {self.price_ratio:.>9}"


class Selling:
    def __init__(self):
        pass
