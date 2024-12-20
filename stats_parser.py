import csv
from typing import Any
from player_data import PlayerData
from match_results import MatchResults

class StatsParser:
    @staticmethod
    def parse_stats_file(file_name: str) -> dict[str, Any]:
        print(f"Parsing file: {file_name}")

        axis_team_name: str = input('Axis Team Name: ')
        allies_team_name: str = input('Allies Team Name: ')
        map_name: str = input('Map Name: ')
        match_date: str = input('Match Date: ')

        armor_player_overrides: set[str] = StatsParser._get_armor_overrides()

        match_results = MatchResults(axis_team_name, allies_team_name, map_name, match_date)
        unknown_weapons = set()

        with open(file_name, encoding="utf8") as f:
            csv_reader = csv.reader(f)
            headers: list[str] = next(csv_reader)  # Read the header row
            
            # Create a dictionary to map column names to indices
            column_indices: dict[str, int] = {column: index for index, column in enumerate(headers)}

            # Determine which ID column is present
            id_column = StatsParser._determine_id_column(column_indices)

            # Check if required columns are present
            required_columns: list[str] = [id_column, 'Name', 'Kills', 'Deaths', 'Combat Effectiveness', 
                                'Offensive Points', 'Defensive Points', 'Support Points', 'Weapons', 'Death by Weapons']
            for column in required_columns:
                if column not in column_indices:
                    print(f"Error: '{column}' column not found in the CSV file.")
                    print("Available columns are:", headers)
                    raise KeyError(f"'{column}' column missing")

            for row in csv_reader:
                try:
                    player = PlayerData(row, column_indices)
                    new_unknown_weapons: set[str] = player.process_weapons()
                    unknown_weapons.update(new_unknown_weapons)
                    player.determine_side_and_group()

                    if player.player_id in armor_player_overrides:
                        player.group = 'Armor'
                        print(f"Setting {player.name} to Armor because of override.")

                    if player.group == 'Infantry' and player.combat_effectiveness > 300 and player.group_likelihood['Infantry'] < 15:
                        StatsParser._prompt_for_armor_classification(player)

                    match_results.add_player(player)
                except Exception as e:
                    print(f"Error processing row: {type(e).__name__} - {e}")
                    print("Row data:", row)
                    raise

        match_results.calculate_kdrs()
        return match_results.to_dict()

    @staticmethod
    def _determine_id_column(column_indices: dict[str, int]) -> str:
        if 'Steam ID' in column_indices:
            return 'Steam ID'
        elif 'Player ID' in column_indices:
            return 'Player ID'
        else:
            raise ValueError("Neither 'Steam ID' nor 'Player ID' found in CSV headers")

    @staticmethod
    def _get_armor_overrides() -> set[str]:
        armor_player_overrides = set()
        while True:
            armor_player_id: str = input('Enter the Player ID or Steam ID of an armor player accidentally being categorized as infantry (leave blank if done entering): ')
            if not armor_player_id:
                break
            armor_player_overrides.add(armor_player_id)
        return armor_player_overrides

    @staticmethod
    def _prompt_for_armor_classification(player: PlayerData) -> None:
        print(f"\nPotential armor player detected: {player.name}")
        print(f"Combat Effectiveness: {player.combat_effectiveness}")
        print(f"Kills: {player.kills}")
        print(f"Deaths: {player.deaths}")
        print(f"K/D Ratio: {player.kdr}")
        print(f"Offensive Points: {player.offensive_points}")
        print(f"Defensive Points: {player.defensive_points}")
        print(f"Support Points: {player.support_points}")
        print("Top weapons:")
        for weapon, count in sorted(player.weapons.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {weapon}: {count}")
        
        response: str = input(f'Based on this information, is {player.name} actually armor? (y/n): ')
        if response.lower() == 'y':
            player.group = 'Armor'
            print('OK, setting this player as Armor')
        else:
            print('Keeping this player as Infantry')