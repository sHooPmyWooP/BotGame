import sqlite3
import xml.etree.ElementTree as ET

import requests

from Classes.PlanetEnemy import PlanetEnemy


class OGameAPI:
    def __init__(self, server_number, language):
        self.server_number = server_number
        self.language = language
        self.planets = []
        self.players = []
        self.planets_players = []

    def get_planets(self):
        self.planets = []
        endpoint = 'universe.xml'
        response = requests.get(f'http://s{self.server_number}-{self.language}.ogame.gameforge.com/api/{endpoint}').text
        universe_root = ET.fromstring(response)
        filtered_uni = universe_root.findall("planet")
        for planet in filtered_uni:
            planet_format = [planet.get("player"), planet.get("coords")]
            self.planets.append(planet_format)

    def get_players(self):
        self.players = []
        endpoint = 'players.xml'
        response = requests.get(f'http://s{self.server_number}-{self.language}.ogame.gameforge.com/api/{endpoint}').text
        player_root = ET.fromstring(response)
        filtered_player = player_root.findall("player")

        for player in filtered_player:
            player_format = [player.get("id"), player.get("status")]
            self.players.append(player_format)

    def map_players_to_planet(self):
        self.get_planets()
        self.get_players()
        # Map Players to Planets
        for player in self.players:
            for planet in self.planets:
                if planet[0] == player[0]:
                    # PlanetEnemy(coords, player_id, status)
                    self.planets_players.append(PlanetEnemy(planet[1], player[0], player[1]))

    def push_inactive_to_db(self):
        self.map_players_to_planet()
        conn = sqlite3.connect('Resources\db\inactive_player.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS INACTIVE_PLAYERS(
        server_number integer,
        player_id integer,
        player_status text,
        planet_coords text);
        """)

        for planet in self.planets_players:
            if planet.status == "I" or planet.status == "i":
                c.execute(f"INSERT INTO INACTIVE_PLAYERS VALUES ('{self.server_number}', '{planet.player_id}',"
                          f" '{planet.status}', '{planet.coords}');")
        conn.commit()
        conn.close()
