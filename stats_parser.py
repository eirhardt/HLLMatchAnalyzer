import csv
import os
from typing import Any
from player_data import PlayerData
from match_results import MatchResults

class StatsParser:
    @staticmethod
    def parse_stats_file(file_name: str) -> dict[str, Any]:
        print(f"Parsing file: {file_name}")

        axis_team_name = input('Axis Team Name: ')
        allies_team_name = input('Allies Team Name: ')
        map_name = input('Map Name: ')
        match_date = input('Match Date: ')

        armor_player_overrides = StatsParser._get_armor_overrides()

        match_results = MatchResults(axis_team_name, allies_team_name, map_name, match_date)
        unknown_weapons = set()

        with open(file_name, encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                player = PlayerData(row)
                new_unknown_weapons = player.process_weapons(row['Death by Weapons'])
                unknown_weapons.update(new_unknown_weapons)
                player.determine_side_and_group()

                if player.steam_id in armor_player_overrides:
                    player.group = 'Armor'
                    print(f"Setting {player.name} to Armor because of override.")

                if player.group == 'Infantry' and player.combat_effectiveness > 300 and player.group_likelihood['Infantry'] < 15:
                    response = input(f'Is {player.name} actually armor? (y/n): ')
                    if response.lower() == 'y':
                        player.group = 'Armor'
                        print('OK, setting this person as Armor')

                match_results.add_player(player)

        match_results.calculate_kdrs()
        return match_results.to_dict()

    @staticmethod
    def _get_armor_overrides() -> set[str]:
        armor_player_overrides = set()
        while True:
            armor_player_id = input('Enter the Steam ID of an armor player accidentally being categorized as infantry (leave blank if done entering): ')
            if not armor_player_id:
                break
            armor_player_overrides.add(armor_player_id)
        return armor_player_overrides

def open_file_explorer(path):
    if os.name == 'nt':  # For Windows
        os.startfile(path)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(('open', path))
    else:
        print(f"Unable to open file explorer for this operating system: {os.name}")