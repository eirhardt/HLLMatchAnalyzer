# This is a Python script that parses the CSV file produced by CRCON that has the stats after a Hell Let Loose match.
# Its purpose is to extract specific details from multiple log files, combining them into one file, for easier comparison of key values

import csv
import json
import time
import os
from typing import Any
import tkinter as tk
from tkinter import filedialog

# Reference data for weapons so we can assign them to a faction
weapons: dict[str, dict[str, str]] = {
    # US Infantry
    'M1A1 THOMPSON': {'side':'Allies','faction':'US','group':'Infantry'},
    'M3 GREASE GUN': {'side':'Allies','faction':'US','group':'Infantry'},
    'M1 GARAND': {'side':'Allies','faction':'US','group':'Infantry'},
    'M1 CARBINE': {'side':'Allies','faction':'US','group':'Infantry'},
    'M1918A2 BAR': {'side':'Allies','faction':'US','group':'Infantry'},
    'M97 TRENCH GUN': {'side':'Allies','faction':'US','group':'Infantry'},
    'BROWNING M1919': {'side':'Allies','faction':'US','group':'Infantry'},
    'M1903 SPRINGFIELD': {'side':'Allies','faction':'US','group':'Infantry'},
    'COLT M1911': {'side':'Allies','faction':'US','group':'Infantry'},
    'M2 FLAMETHROWER': {'side':'Allies','faction':'US','group':'Infantry'},
    'M3 KNIFE': {'side':'Allies','faction':'US','group':'Infantry'},
    'MK2 GRENADE': {'side':'Allies','faction':'US','group':'Infantry'},
    'M2 AP MINE': {'side':'Allies','faction':'US','group':'Infantry'},
    'M1A1 AT MINE': {'side':'Allies','faction':'US','group':'Infantry'},
    'BAZOOKA': {'side':'Allies','faction':'US','group':'Infantry'},
    '57MM CANNON [M1 57mm]': {'side':'Allies','faction':'US','group':'Infantry'},
    'M3 Half-track': {'side':'Allies','faction':'US','group':'Infantry'},
    'M2 Browning [M3 Half-track]': {'side':'Allies','faction':'US','group':'Infantry'},
    'GMC CCKW 353 (Transport)': {'side':'Allies','faction':'US','group':'Infantry'},
    'GMC CCKW 353 (Supply)': {'side':'Allies','faction':'US','group':'Infantry'},
    'Jeep Willys': {'side':'Allies','faction':'US','group':'Infantry'},

    # US Artillery
    '155MM HOWITZER [M114]': {'side':'Allies','faction':'US','group':'Artillery'},

    # US Armor
    'M8 Greyhound': {'side':'Allies','faction':'US','group':'Armor'},
    'M6 37mm [M8 Greyhound]': {'side':'Allies','faction':'US','group':'Armor'},
    'COAXIAL M1919 [M8 Greyhound]': {'side':'Allies','faction':'US','group':'Armor'},
    'Stuart M5A1': {'side':'Allies','faction':'US','group':'Armor'},
    '37MM CANNON [Stuart M5A1]': {'side':'Allies','faction':'US','group':'Armor'},
    'COAXIAL M1919 [Stuart M5A1]': {'side':'Allies','faction':'US','group':'Armor'},
    'HULL M1919 [Stuart M5A1]': {'side':'Allies','faction':'US','group':'Armor'},
    'Sherman M4A3(75)W': {'side':'Allies','faction':'US','group':'Armor'},
    '75MM CANNON [Sherman M4A3(75)W]': {'side':'Allies','faction':'US','group':'Armor'},
    'COAXIAL M1919 [Sherman M4A3(75)W]': {'side':'Allies','faction':'US','group':'Armor'},
    'HULL M1919 [Sherman M4A3(75)W]': {'side':'Allies','faction':'US','group':'Armor'},
    'Sherman M4A3E2': {'side':'Allies','faction':'US','group':'Armor'},
    '75MM M3 GUN [Sherman M4A3E2]': {'side':'Allies','faction':'US','group':'Armor'},
    'COAXIAL M1919 [Sherman M4A3E2]': {'side':'Allies','faction':'US','group':'Armor'},
    'HULL M1919 [Sherman M4A3E2]': {'side':'Allies','faction':'US','group':'Armor'},
    'Sherman M4A3E2(76)': {'side':'Allies','faction':'US','group':'Armor'},
    '76MM M1 GUN [Sherman M4A3E2(76)]': {'side':'Allies','faction':'US','group':'Armor'},
    'COAXIAL M1919 [Sherman M4A3E2(76)]': {'side':'Allies','faction':'US','group':'Armor'},
    'HULL M1919 [Sherman M4A3E2(76)]': {'side':'Allies','faction':'US','group':'Armor'},

    # GER Infantry
    'MP40': {'side':'Axis','faction':'GER','group':'Infantry'},
    'GEWEHR 43': {'side':'Axis','faction':'GER','group':'Infantry'},
    'KARABINER 98K': {'side':'Axis','faction':'GER','group':'Infantry'},
    'STG44': {'side':'Axis','faction':'GER','group':'Infantry'},
    'FG42': {'side':'Axis','faction':'GER','group':'Infantry'},
    'MG34': {'side':'Axis','faction':'GER','group':'Infantry'},
    'MG42': {'side':'Axis','faction':'GER','group':'Infantry'},
    'KARABINER 98K x8': {'side':'Axis','faction':'GER','group':'Infantry'},
    'FG42 x4': {'side':'Axis','faction':'GER','group':'Infantry'},
    'WALTHER P38': {'side':'Axis','faction':'GER','group':'Infantry'},
    'LUGER P08': {'side':'Axis','faction':'GER','group':'Infantry'},
    'FLAMMENWERFER 41': {'side':'Axis','faction':'GER','group':'Infantry'},
    'FELDSPATEN': {'side':'Axis','faction':'GER','group':'Infantry'},
    'M24 STIELHANDGRANATE': {'side':'Axis','faction':'GER','group':'Infantry'},
    'M43 STIELHANDGRANATE': {'side':'Axis','faction':'GER','group':'Infantry'},
    'S-MINE': {'side':'Axis','faction':'GER','group':'Infantry'},
    'TELLERMINE 43': {'side':'Axis','faction':'GER','group':'Infantry'},
    'PANZERSCHRECK': {'side':'Axis','faction':'GER','group':'Infantry'},
    '75MM CANNON [PAK 40]': {'side':'Axis','faction':'GER','group':'Infantry'},
    'Sd.Kfz 251 Half-track': {'side':'Axis','faction':'GER','group':'Infantry'},
    'MG 42 [Sd.Kfz 251 Half-track]': {'side':'Axis','faction':'GER','group':'Infantry'},
    'Opel Blitz (Transport)': {'side':'Axis','faction':'GER','group':'Infantry'},
    'Opel Blitz (Supply)': {'side':'Axis','faction':'GER','group':'Infantry'},
    'Kubelwagen': {'side':'Axis','faction':'GER','group':'Infantry'},

    # GER Artillery
    '150MM HOWITZER [sFH 18]': {'side':'Axis','faction':'GER','group':'Artillery'},

    # GER Armor
    'Sd.Kfz.234 Puma': {'side':'Axis','faction':'GER','group':'Armor'},
    '50mm KwK 39/1 [Sd.Kfz.234 Puma]': {'side':'Axis','faction':'GER','group':'Armor'},
    'COAXIAL MG34 [Sd.Kfz.234 Puma]': {'side':'Axis','faction':'GER','group':'Armor'},
    'Sd.Kfz.121 Luchs': {'side':'Axis','faction':'GER','group':'Armor'},
    '20MM KWK 30 [Sd.Kfz.121 Luchs]': {'side':'Axis','faction':'GER','group':'Armor'},
    'COAXIAL MG34 [Sd.Kfz.121 Luchs]': {'side':'Axis','faction':'GER','group':'Armor'},
    'Sd.Kfz.161 Panzer IV': {'side':'Axis','faction':'GER','group':'Armor'},
    '75MM CANNON [Sd.Kfz.161 Panzer IV]': {'side':'Axis','faction':'GER','group':'Armor'},
    'COAXIAL MG34 [Sd.Kfz.161 Panzer IV]': {'side':'Axis','faction':'GER','group':'Armor'},
    'HULL MG34 [Sd.Kfz.161 Panzer IV]': {'side':'Axis','faction':'GER','group':'Armor'},
    'Sd.Kfz.181 Tiger 1': {'side':'Axis','faction':'GER','group':'Armor'},
    '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]': {'side':'Axis','faction':'GER','group':'Armor'},
    'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]': {'side':'Axis','faction':'GER','group':'Armor'},
    'HULL MG34 [Sd.Kfz.181 Tiger 1]': {'side':'Axis','faction':'GER','group':'Armor'},
    'Sd.Kfz.171 Panther': {'side':'Axis','faction':'GER','group':'Armor'},
    '75MM CANNON [Sd.Kfz.171 Panther]': {'side':'Axis','faction':'GER','group':'Armor'},
    'COAXIAL MG34 [Sd.Kfz.171 Panther]': {'side':'Axis','faction':'GER','group':'Armor'},
    'HULL MG34 [Sd.Kfz.171 Panther]': {'side':'Axis','faction':'GER','group':'Armor'},

    # RUS Infantry
    'PPSH 41': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'PPSH 41 W/DRUM': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'SVT40': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'MOSIN NAGANT 1891': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'MOSIN NAGANT 91/30': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'MOSIN NAGANT M38': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'DP-27': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'SCOPED MOSIN NAGANT 91/30': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'SCOPED SVT40': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'NAGANT M1895': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'TOKAREV TT33': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'MPL-50 SPADE': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'RG-42 GRENADE': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'MOLOTOV': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'POMZ AP MINE': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'TM-35 AT MINE': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'PTRS-41': {'side':'Allies','faction':'RUS','group':'Infantry'},
    # BAZOOKA is already categorized as US
    '57MM CANNON [ZiS-2]': {'side':'Allies','faction':'RUS','group':'Infantry'},
    # M3 Half-track is already categorized as US
    'ZIS-5 (Transport)': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'ZIS-5 (Supply)': {'side':'Allies','faction':'RUS','group':'Infantry'},
    'GAZ-67': {'side':'Allies','faction':'RUS','group':'Infantry'},

    # RUS Artillery
    '122MM HOWITZER [M1938 (M-30)]': {'side':'Allies','faction':'RUS','group':'Artillery'},

    # RUS Armor
    'BA-10': {'side':'Allies','faction':'RUS','group':'Armor'},
    '19-K 45MM [BA-10]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'COAXIAL DT [BA-10]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'T70': {'side':'Allies','faction':'RUS','group':'Armor'},
    '45MM M1937 [T70]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'COAXIAL DT [T70]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'T34/76': {'side':'Allies','faction':'RUS','group':'Armor'},
    '76MM ZiS-5 [T34/76]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'COAXIAL DT [T34/76]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'HULL DT [T34/76]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'IS-1': {'side':'Allies','faction':'RUS','group':'Armor'},
    'D-5T 85MM [IS-1]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'COAXIAL DT [IS-1]': {'side':'Allies','faction':'RUS','group':'Armor'},
    'HULL DT [IS-1]': {'side':'Allies','faction':'RUS','group':'Armor'},

    # GB Infantry
    'Sten Gun Mk.II': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Sten Gun Mk.V': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Lanchester': {'side':'Allies','faction':'GB','group':'Infantry'},
    'M1928A1 THOMPSON': {'side':'Allies','faction':'GB','group':'Infantry'},
    'SMLE No.1 Mk III': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Rifle No.4 Mk I': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Rifle No.5 Mk I': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Bren Gun': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Lewis Gun': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Lee-Enfield Pattern 1914 Sniper': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Rifle No.4 Mk I Sniper': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Webley MK VI': {'side':'Allies','faction':'GB','group':'Infantry'},
    'FLAMETHROWER': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Fairbairn–Sykes': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Mills Bomb': {'side':'Allies','faction':'GB','group':'Infantry'},
    'No.82 Grenade': {'side':'Allies','faction':'GB','group':'Infantry'},
    'A.P. Shrapnel Mine Mk II': {'side':'Allies','faction':'GB','group':'Infantry'},
    'A.T. Mine G.S. Mk V': {'side':'Allies','faction':'GB','group':'Infantry'},
    'PIAT': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Boys Anti-tank Rifle': {'side':'Allies','faction':'GB','group':'Infantry'},
    'QF 6-POUNDER [QF 6-Pounder]': {'side':'Allies','faction':'GB','group':'Infantry'},
    # M3 Half-track is already categorized as US
    'Bedford OYD (Transport)': {'side':'Allies','faction':'GB','group':'Infantry'},
    'Bedford OYD (Supply)': {'side':'Allies','faction':'GB','group':'Infantry'},
    # Jeep Willys is already categorized as US

    # GB Artillery
    'QF 25-POUNDER [QF 25-Pounder]': {'side':'Allies','faction':'GB','group':'Artillery'},

    # GB Armor
    'Daimler': {'side':'Allies','faction':'GB','group':'Armor'},
    'QF 2-POUNDER [Daimler]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA [Daimler]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Tetrarch': {'side':'Allies','faction':'GB','group':'Armor'},
    'QF 2-POUNDER [Tetrarch]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA [Tetrarch]': {'side':'Allies','faction':'GB','group':'Armor'},
    'M3 Stuart Honey': {'side':'Allies','faction':'GB','group':'Armor'},
    '37MM CANNON [M3 Stuart Honey]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL M1919 [M3 Stuart Honey]': {'side':'Allies','faction':'GB','group':'Armor'},
    'HULL M1919 [M3 Stuart Honey]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Cromwell': {'side':'Allies','faction':'GB','group':'Armor'},
    'QF 75MM [Cromwell]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA [Cromwell]': {'side':'Allies','faction':'GB','group':'Armor'},
    'HULL BESA [Cromwell]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Crusader Mk.III': {'side':'Allies','faction':'GB','group':'Armor'},
    'OQF 57MM [Crusader Mk.III]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA [Crusader Mk.III]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Firefly': {'side':'Allies','faction':'GB','group':'Armor'},
    'QF 17-POUNDER [Firefly]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL M1919 [Firefly]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Churchill Mk.III': {'side':'Allies','faction':'GB','group':'Armor'},
    'OQF 57MM [Churchill Mk.III]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA 7.92mm [Churchill Mk.III]': {'side':'Allies','faction':'GB','group':'Armor'},
    'HULL BESA 7.92mm [Churchill Mk.III]': {'side':'Allies','faction':'GB','group':'Armor'},
    'Churchill Mk.VII': {'side':'Allies','faction':'GB','group':'Armor'},
    'OQF 57MM [Churchill Mk.VII]': {'side':'Allies','faction':'GB','group':'Armor'},
    'COAXIAL BESA 7.92mm [Churchill Mk.VII]': {'side':'Allies','faction':'GB','group':'Armor'},
    'HULL BESA 7.92mm [Churchill Mk.VII]': {'side':'Allies','faction':'GB','group':'Armor'}
}

machine_guns: set[str] = {
    'BROWNING M1919', 'MG34', 'MG42', 'DP-27', 'Lewis Gun'
}

# Define a type alias for the complex structure returned by parse_stats_file
StatsResult = dict[str, Any]

# Define a type for the values that can be stored in the results dictionary
ResultValue = set[str] | StatsResult

# Start a dictionary to store our results in, each log file parsed will be a single entry in results
results: dict[str, ResultValue] = {
    'unknownWeapons': set()
}

def calculate_kdr(kills: int, deaths: int) -> str:
    denominator = 1 if deaths == 0 else deaths
    return format(kills / denominator, '.2f')

def parse_player_data(row: dict[str, str], armor_player_overrides: set[str]) -> tuple[dict[str, Any], set[str]]:
    unknown_weapons = set()

    player = {
        'SteamID': row['Steam ID'],
        'Name': row['Name'],
        'Kills': int(row['Kills']),
        'Deaths': int(row['Deaths']),
        'KDR': calculate_kdr(int(row['Kills']), int(row['Deaths'])),
        'CombatEffectiveness': int(row['Combat Effectiveness']),
        'OffensivePoints': int(row['Offensive Points']),
        'DefensivePoints': int(row['Defensive Points']),
        'SupportPoints': int(row['Support Points']),
        'Weapons': row['Weapons'],
        'MachineGunKills': 0
    }

    side_likelihood = {
        'Axis': 0,
        'Allies': 0
    }

    group_likelihood = {
        'Infantry': 0,
        'Artillery': 0,
        'Armor': 0
    }

    # We look at the weapons used by each player to infer what side they played, and if they played mostly infantry, armor, or artillery
    for weapon, count in json.loads(player['Weapons']).items():
        count = int(count)
        if weapon in weapons:
            ref = weapons[weapon]
            side_likelihood[ref['side']] += count
            group_likelihood[ref['group']] += count
        else:
            unknown_weapons.add(weapon)
        if weapon in machine_guns:
            player['MachineGunKills'] += count

    # We look at the weapons used against each player as part of inferring what side they played on
    for weapon, count in json.loads(row['Death by Weapons']).items():
        count = int(count)
        if weapon in weapons:
            ref = weapons[weapon]
            side_inverse = 'Axis' if ref['side'] == 'Allies' else 'Allies'
            side_likelihood[side_inverse] += count
        else:
            unknown_weapons.add(weapon)

    # Decide what side and group this player belongs to
    player['sideLikelihood'] = side_likelihood
    player['groupLikelihood'] = group_likelihood
    player['Side'] = 'Spectators' if side_likelihood['Axis'] == 0 and side_likelihood['Allies'] == 0 else 'Allies' if side_likelihood['Allies'] > side_likelihood['Axis'] else 'Axis'
    group_name = max(group_likelihood, key=lambda k: group_likelihood[k])
    player['Group'] = group_name

    # Potentially override if we know for sure this player is armor
    if player['SteamID'] in armor_player_overrides:
        player['Group'] = 'Armor'
        print(f"Setting {player['Name']} to Armor because of override.")

    # Little tweak to hopefully pull armor spotters out of Unknown, since they almost never have any kills
    if group_name == 'Unknown' and player['CombatEffectiveness'] > 100:
        player['Group'] = 'Armor'

    print(player)

    # Try to find tankers that got no armor weapon kills, got infantry kills; these look like inf players but the combat effectiveness is too high
    if player['Group'] == 'Infantry' and player['CombatEffectiveness'] > 300 and player['groupLikelihood']['Infantry'] < 15:
        response = input('Is this player actually armor? (y/n): ')
        if response.lower() == 'y':
            player['Group'] = 'Armor'
            print('OK, setting this person as Armor')

    return player, unknown_weapons

def parse_stats_file(file_name: str) -> StatsResult:    
    print(file_name)

    # Collect basic metadata about the match
    axis_team_name = input('Axis Team Name: ')
    allies_team_name = input('Allies Team Name: ')
    map_name = input('Map Name: ')
    match_date = input('Match Date: ')

    # Sometimes it's not obvious that someone is armor, so we ask the user for any overrides
    armor_player_overrides = set()
    unknown_weapons = set()
    while True:
        armor_player_id = input('Enter the Steam ID of an armor player accidentally being categorized as infantry (leave blank if done entering): ')
        if not armor_player_id:
            break
        armor_player_overrides.add(armor_player_id)

    
    
    with open(file_name, encoding="utf8") as f:
        match_results = {
            'Axis': {
                'Team Name': axis_team_name,
                'Total': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'MachineGunKills': 0
                },
                'Infantry': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Artillery': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Armor': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Unknown': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                }
            },
            'Allies': {
                'Team Name': allies_team_name,
                'Total': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'MachineGunKills': 0
                },
                'Infantry': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Artillery': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Armor': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Unknown': {
                    'PlayerCount': 0,
                    'Kills': 0,
                    'Deaths': 0,
                    'KDR': 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                }
            },
            'Spectators': [],
            'Map': map_name,
            'Match Date': match_date
        }

        # get the csv data
        reader = csv.DictReader(f)
        for row in reader:
            player, new_unknown_weapons = parse_player_data(row, armor_player_overrides)
            unknown_weapons.update(new_unknown_weapons)
            
            if player['Side'] == 'Spectators':
                match_results['Spectators'].append(player)
            else:
                side = match_results[player['Side']]
                group = side[player['Group']]
                group['PlayerCount'] += 1
                group['Kills'] += player['Kills']
                group['Deaths'] += player['Deaths']
                group['CombatEffectiveness'] += player['CombatEffectiveness']
                group['OffensivePoints'] += player['OffensivePoints']
                group['DefensivePoints'] += player['DefensivePoints']
                group['SupportPoints'] += player['SupportPoints']
                group['Players'].append(player)
                side['Total']['PlayerCount'] += 1
                side['Total']['Kills'] += player['Kills']
                side['Total']['Deaths'] += player['Deaths']
                side['Total']['CombatEffectiveness'] += player['CombatEffectiveness']
                side['Total']['OffensivePoints'] += player['OffensivePoints']
                side['Total']['DefensivePoints'] += player['DefensivePoints']
                side['Total']['SupportPoints'] += player['SupportPoints']
                side['Total']['MachineGunKills'] += player['MachineGunKills']

    # calculate KDRs
    match_results['Axis']['Total']['KDR'] = calculate_kdr(match_results['Axis']['Total']['Kills'], match_results['Axis']['Total']['Deaths'])
    match_results['Axis']['Infantry']['KDR'] = calculate_kdr(match_results['Axis']['Infantry']['Kills'], match_results['Axis']['Infantry']['Deaths'])
    match_results['Axis']['Artillery']['KDR'] = calculate_kdr(match_results['Axis']['Artillery']['Kills'], match_results['Axis']['Artillery']['Deaths'])
    match_results['Axis']['Armor']['KDR'] = calculate_kdr(match_results['Axis']['Armor']['Kills'], match_results['Axis']['Armor']['Deaths'])
    match_results['Axis']['Unknown']['KDR'] = calculate_kdr(match_results['Axis']['Unknown']['Kills'], match_results['Axis']['Unknown']['Deaths'])
    match_results['Allies']['Total']['KDR'] = calculate_kdr(match_results['Allies']['Total']['Kills'], match_results['Allies']['Total']['Deaths'])
    match_results['Allies']['Infantry']['KDR'] = calculate_kdr(match_results['Allies']['Infantry']['Kills'], match_results['Allies']['Infantry']['Deaths'])
    match_results['Allies']['Artillery']['KDR'] = calculate_kdr(match_results['Allies']['Artillery']['Kills'], match_results['Allies']['Artillery']['Deaths'])
    match_results['Allies']['Armor']['KDR'] = calculate_kdr(match_results['Allies']['Armor']['Kills'], match_results['Allies']['Armor']['Deaths'])
    match_results['Allies']['Unknown']['KDR'] = calculate_kdr(match_results['Allies']['Unknown']['Kills'], match_results['Allies']['Unknown']['Deaths'])

    # return results
    return match_results

def open_file_explorer(path):
    if os.name == 'nt':  # For Windows
        os.startfile(path)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(('open', path))
    else:
        print(f"Unable to open file explorer for this operating system: {os.name}")

def main():
    print("Welcome to the Hell Let Loose Stats Parser!")
    print("This script will parse CSV files produced by CRCON after a Hell Let Loose match.")

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    print("\nPlease select the CSV file you want to parse.")
    file_path = filedialog.askopenfilename(
        title="Select CSV file to parse",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not file_path:  # User cancelled the file dialog
        print("No file selected. Exiting.")
        return

    file_name = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    print(f"\nParsing file: {file_path}")
    
    try:
        parsed_results = parse_stats_file(file_path)
        print(f"Successfully parsed {file_name}")

        # Write the detailed results to a JSON file in the same directory
        output_file = os.path.join(directory, f'matchAnalysisResults_{int(time.time())}.json')
        with open(output_file, 'w') as f:
            json.dump(parsed_results, f, indent=2)
        print(f"\nResults have been saved to {output_file}")

        # Open file explorer to the directory of the parsed file
        open_file_explorer(directory)

    except Exception as e:
        print(f"Error parsing {file_name}: {type(e).__name__} - {e}")

    print("\nThank you for using the Hell Let Loose Stats Parser!")
    print("The file explorer has been opened to the location of the parsed file.")
    print("The program will now close.")

if __name__ == "__main__":
    main()


