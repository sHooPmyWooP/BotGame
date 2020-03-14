import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from Classes.PlanetEnemy import PlanetEnemy


class OGameAPI:
    """
    Interact with OGames API: http://s{server_number}-{language}.ogame.gameforge.com/api/{endpoint}
    Endpoints:
    players.xml (1 day): Contain list of all players on the server along with their names and status.
    alliances.xml (1 day): Contain list of all alliances on the server along with their members, name and tag.
    serverData.xml (1 day): Contain information about server properties such as name, language, speed, debris etc.
    universe.xml (1 week): Contain list of all planets on the server along with their names, coordinates and owners.
    highscore.xml (1 hour): Contain statistics of various types about players and alliances on the server.
    """

    def __init__(self, server_number, language):
        """
        :param server_number: int
        :param language: str
        """
        self.server_number = server_number
        self.language = language
        self.planets = []
        self.players = []
        self.planets_players = []

    def get_planets(self):
        """
        Get all planets from server updated to self.planets
        :return: None
        """
        self.planets = []
        endpoint = 'universe.xml'
        response = requests.get(f'http://s{self.server_number}-{self.language}.ogame.gameforge.com/api/{endpoint}').text
        universe_root = ET.fromstring(response)
        filtered_uni = universe_root.findall("planet")
        for planet in filtered_uni:
            planet_format = [planet.get("player"), planet.get("coords")]
            self.planets.append(planet_format)

    def get_players(self):
        """
        Get all players from server updated to self.players
        :return: None
        """
        self.players = []
        endpoint = 'players.xml'
        response = requests.get(f'http://s{self.server_number}-{self.language}.ogame.gameforge.com/api/{endpoint}').text
        player_root = ET.fromstring(response)
        filtered_player = player_root.findall("player")

        for player in filtered_player:
            player_format = [player.get("id"), player.get("status")]
            self.players.append(player_format)

    def map_players_to_planet(self):
        """
        Join Planets with Players and thus get the ability to e.g. filter for inactive targets
        :return: None
        """
        self.get_planets()
        self.get_players()
        # Map Players to Planets
        for player in self.players:
            for planet in self.planets:
                if planet[0] == player[0]:
                    # PlanetEnemy(coords, player_id, status)
                    self.planets_players.append(PlanetEnemy(planet[1], player[0], player[1]))

    def push_inactive_to_db(self):
        """
        Filter Planets for Inactive PLayers and push those to inactive_players.db.
        Tables in that DB: INACTIVE_PLAYERS (server_number, player_id, player_status, planet_coords, timestamp)
        :return: None
        """
        self.map_players_to_planet()
        conn = sqlite3.connect('Resources\db\inactive_players.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS INACTIVE_PLAYERS(
        server_number integer,
        player_id integer,
        player_status text,
        planet_coords text,
        timestamp datetime default current_timestamp);
        """)
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for planet in self.planets_players:
            if planet.status == "I" or planet.status == "i":
                statement = "INSERT INTO 'INACTIVE_PLAYERS' VALUES (?, ?, ?,?,?);"
                tuple = (self.server_number, planet.player_id, planet.status, planet.coords, current_timestamp)
                c.execute(statement, tuple)
        conn.commit()
        conn.close()
