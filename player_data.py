import json
from typing import Any, Literal

from weapon_data import WeaponData

class PlayerData:
    def __init__(self, row: dict[str, str]):
        self.steam_id = row['Steam ID']
        self.name: str = row['Name']
        self.kills = int(row['Kills'])
        self.deaths = int(row['Deaths'])
        self.kdr: str = self.calculate_kdr()
        self.combat_effectiveness = int(row['Combat Effectiveness'])
        self.offensive_points = int(row['Offensive Points'])
        self.defensive_points = int(row['Defensive Points'])
        self.support_points = int(row['Support Points'])
        self.weapons = row['Weapons']
        self.machine_gun_kills = 0
        self.side_likelihood: dict[str, int] = {'Axis': 0, 'Allies': 0}
        self.group_likelihood: dict[str, int] = {'Infantry': 0, 'Artillery': 0, 'Armor': 0}
        self.side = 'Spectators'
        self.group = 'Unknown'

    def calculate_kdr(self) -> str:
        denominator = 1 if self.deaths == 0 else self.deaths
        return format(self.kills / denominator, '.2f')

    def process_weapons(self, death_by_weapons: str) -> set[str]:
        unknown_weapons = set()
        
        for weapon, count in json.loads(self.weapons).items():
            count = int(count)
            if weapon in WeaponData.WEAPONS:
                ref = WeaponData.WEAPONS[weapon]
                self.side_likelihood[ref['side']] += count
                self.group_likelihood[ref['group']] += count
            else:
                unknown_weapons.add(weapon)
            if weapon in WeaponData.MACHINE_GUNS:
                self.machine_gun_kills += count

        for weapon, count in json.loads(death_by_weapons).items():
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
            'MachineGunKills': self.machine_gun_kills,
            'sideLikelihood': self.side_likelihood,
            'groupLikelihood': self.group_likelihood,
            'Side': self.side,
            'Group': self.group
        }
