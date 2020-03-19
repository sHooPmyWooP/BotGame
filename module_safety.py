import datetime
import winsound
from time import sleep

from Classes.Account import Account


def sos():
    for i in range(0, 3):
        winsound.Beep(2000, 100)
        for i in range(0, 3):
            winsound.Beep(2000, 400)
            for i in range(0, 3):
                winsound.Beep(2000, 100)


def safety_module(sound=False):
    while True:
        time_to_sleep = 180
        try:
            acc = Account("Octans", "david-achilles@hotmail.de", "OGame!4friends")
            if acc.chk_get_attacked():
                if sound:
                    sos()
                acc.read_in_all_planets()
                for planet in acc.planets:
                    planet.build_defense_routine(1000)
            else:
                sleep_until = datetime.datetime.now() + datetime.timedelta(0, time_to_sleep)
                print("Sleep until:", sleep_until)
                sleep(time_to_sleep)
        except:
            print("Exception! Sleeping 60 Seconds before retry.")
            if sound:
                sos()
            sleep(time_to_sleep)


safety_module()
