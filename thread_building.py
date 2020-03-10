from Classes.Account import Account


def get_next_building(acc):
    print(acc.planets[0].buildings["Metallmine"].level)


a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")
a1.login()
get_next_building(a1)
