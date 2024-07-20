import json
from typing import Any

from weapon_data import WeaponData

class PlayerData:
    def __init__(self, row: list[str], column_indices: dict[str, int]):
        self.steam_id = row[column_indices['Steam ID']]
        self.name = row[column_indices['Name']]  # Use the name as-is, without decoding
        self.kills = int(row[column_indices['Kills']])
        self.deaths = int(row[column_indices['Deaths']])
        self.kdr = self.calculate_kdr()
        self.combat_effectiveness = int(row[column_indices['Combat Effectiveness']])
        self.offensive_points = int(row[column_indices['Offensive Points']])
        self.defensive_points = int(row[column_indices['Defensive Points']])
        self.support_points = int(row[column_indices['Support Points']])
        self.weapons = self.parse_json_field(row[column_indices['Weapons']])
        self.death_by_weapons = self.parse_json_field(row[column_indices['Death by Weapons']])
        self.machine_gun_kills = 0
        self.side_likelihood = {'Axis': 0, 'Allies': 0}
        self.group_likelihood = {'Infantry': 0, 'Artillery': 0, 'Armor': 0}
        self.side = 'Spectators'
        self.group = 'Unknown'

    
    @staticmethod
    def parse_json_field(field: str) -> dict[str, int]:
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON field: {field}")
            return {}

    def calculate_kdr(self) -> str:
        denominator = 1 if self.deaths == 0 else self.deaths
        return format(self.kills / denominator, '.2f')

    def process_weapons(self) -> set[str]:
        unknown_weapons = set()
        
        for weapon, count in self.weapons.items():
            count = int(count)
            if weapon in WeaponData.WEAPONS:
                ref: dict[str, str] = WeaponData.WEAPONS[weapon]
                self.side_likelihood[ref['side']] += count
                self.group_likelihood[ref['group']] += count
            else:
                unknown_weapons.add(weapon)
            if weapon in WeaponData.MACHINE_GUNS:
                self.machine_gun_kills += count

        for weapon, count in self.death_by_weapons.items():
            count = int(count)
            if weapon in WeaponData.WEAPONS:
                ref = WeaponData.WEAPONS[weapon]
                side_inverse = 'Axis' if ref['side'] == 'Allies' else 'Allies'
                self.side_likelihood[side_inverse] += count
            else:
                unknown_weapons.add(weapon)

        return unknown_weapons

    def determine_side_and_group(self) -> None:
        if self.side_likelihood['Axis'] == 0 and self.side_likelihood['Allies'] == 0:
            self.side = 'Spectators'
        else:
            self.side = 'Allies' if self.side_likelihood['Allies'] > self.side_likelihood['Axis'] else 'Axis'
        
        if self.group_likelihood:
            self.group = max(self.group_likelihood, key=lambda k: self.group_likelihood[k])
        else:
            self.group = 'Unknown'

        if self.group == 'Unknown' and self.combat_effectiveness > 100:
            self.group = 'Armor'

    def to_dict(self) -> dict[str, Any]:
        return {
            'SteamID': self.steam_id,
            'Name': self.name,
            'Kills': self.kills,
            'Deaths': self.deaths,
            'KDR': self.kdr,
            'CombatEffectiveness': self.combat_effectiveness,
            'OffensivePoints': self.offensive_points,
            'DefensivePoints': self.defensive_points,
            'SupportPoints': self.support_points,
            'Weapons': self.weapons,
            'DeathByWeapons': self.death_by_weapons,
            'MachineGunKills': self.machine_gun_kills,
            'sideLikelihood': self.side_likelihood,
            'groupLikelihood': self.group_likelihood,
            'Side': self.side,
            'Group': self.group
        }
