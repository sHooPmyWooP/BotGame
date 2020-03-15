from Classes.Account import *
from Classes.Routines import *

if __name__ == "__main__":
    a1 = Account(universe="Octans", username="david-achilles@hotmail.de", password="OGame!4friends")
    send_max_expeditions(a1)
    print("Done...")