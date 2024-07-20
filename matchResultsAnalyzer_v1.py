# This is a Python script that parses the CSV file produced by CRCON that has the stats after a Hell Let Loose match.
# Its purpose is to extract specific details from multiple log files, combining them into one file, for easier comparison of key values
# To use, select one or more JSON files produced by GW2EI and drag and drop them onto this script file using your file explorer

import csv, json, sys, pandas, time, os

# Reference data for weapons so we can assign them to a faction
weapons = {

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
    '': {'side':'Allies','faction':'GB','group':'Infantry'},

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

machineGuns = {
    'BROWNING M1919', 'MG34', 'MG42', 'DP-27', 'Lewis Gun'
}

# Start a dictionary to store our results in, each log file parsed will be a single entry in results
results = {
    'unknownWeapons': set()
}

# Function for calculating a KDR
def calculateKDR(kills, deaths):
    denom = 1 if int(deaths) == 0 else deaths
    return format(int(kills) / int(denom), '.2f')

# Function for parsing out a single player's data
def parsePlayerData(row, armorPlayerOverrides):

    player = {
        'SteamID': row['Steam ID'],
        'Name': row['Name'],
        'Kills': int(row['Kills']),
        'Deaths': int(row['Deaths']),
        'KDR': calculateKDR(row['Kills'],row['Deaths']),
        'CombatEffectiveness': int(row['Combat Effectiveness']),
        'OffensivePoints': int(row['Offensive Points']),
        'DefensivePoints': int(row['Defensive Points']),
        'SupportPoints': int(row['Support Points']),
        'Weapons': row['Weapons'],
        'MachineGunKills': 0
    }

    sideLikelihood = {
        'Axis' : 0,
        'Allies' : 0
    }

    groupLikelihood = {
        'Infantry' : 0,
        'Artillery' : 0,
        'Armor' : 0
    }

    # We look at the weapons used by each player to infer what side they played, and if they played mostly infantry, armor, or artillery
    for weapon, count in json.loads(player['Weapons']).items():
        if weapon in weapons:
            ref = weapons[weapon]
            sideLikelihood[ref['side']] += count
            groupLikelihood[ref['group']] += count
        else:
            results['unknownWeapons'].add(weapon)
        if weapon in machineGuns:
            player['MachineGunKills'] += count

    # We look at the weapons used against each player as part of inferring what side they played on
    for weapon, count in json.loads(row['Death by Weapons']).items():
        if weapon in weapons:
            ref = weapons[weapon]
            sideInverse = 'Axis' if ref['side'] == 'Allies' else 'Allies'
            sideLikelihood[sideInverse] += count
        else:
            results['unknownWeapons'].add(weapon)

    # Decide what side and group this player belongs to
    player['sideLikelihood'] = sideLikelihood
    player['groupLikelihood'] = groupLikelihood
    player['Side'] = 'Spectators' if sideLikelihood['Axis'] == 0 and sideLikelihood['Allies'] == 0 else 'Allies' if sideLikelihood['Allies'] > sideLikelihood['Axis'] else 'Axis'
    groupName = 'Unknown'
    groupScore = 0
    for group, score in groupLikelihood.items():
        if score > groupScore:
            groupScore = score
            groupName = group
    player['Group'] = groupName

    # Potentially override if we know for sure this player is armor
    if player['SteamID'] in armorPlayerOverrides:
        player['Group'] = 'Armor'
        print('Setting ' + player['Name'] + ' to Armor because of override.')

    # Little tweak to hopefully pull armor spotters out of Unknown, since they almost never have any kills
    if groupName == 'Unknown' and player['CombatEffectiveness'] > 100:
        player['Group'] = 'Armor'

    print(player)

    # Try to find tankers that got no armor weapon kills, got infantry kills; these look like inf players but the combat effectiveness is too high
    if player['Group'] == 'Infantry' and player['CombatEffectiveness'] > 300 and player['groupLikelihood']['Infantry'] < 15:
        response = input('Is this player actually armor? (y/n): ')
        if response == 'y':
            player['Group'] = 'Armor'
            print('OK, setting this person as Armor')

    return player

# Function for breaking down a stats file into just the parts we care about
def parseStatsFile(fileName):
    print(fileName)

    # Collect basic metadata about the match
    axisTeamName = input('Axis Team Name: ')
    alliesTeamName = input('Allies Team Name: ')
    mapName = input('Map Name: ')
    matchDate = input('Match Date: ')

    # Sometimes it's not obvious that someone is armor, so we ask the user for any overrides
    armorPlayerOverrides = set()
    while True:
        armorPlayerId = input('Enter the Steam ID of an armor player accidentally being categorized as infantry (leave blank if done entering): ')
        if(armorPlayerId):
            armorPlayerOverrides.add(armorPlayerId)
        else:
            break
    
    with open(fileName, encoding="utf8") as f:

        matchResults = {
            'Axis' : {
                'Team Name' : axisTeamName,
                'Total' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'MachineGunKills' : 0
                },
                'Infantry' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Artillery' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Armor' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Unknown' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                }
            },
            'Allies' : {
                'Team Name' : alliesTeamName,
                'Total' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'MachineGunKills': 0
                },
                'Infantry' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Artillery' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Armor' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                },
                'Unknown' : {
                    'PlayerCount' : 0,
                    'Kills' : 0,
                    'Deaths' : 0,
                    'KDR' : 0.0,
                    'CombatEffectiveness': 0,
                    'OffensivePoints': 0,
                    'DefensivePoints': 0,
                    'SupportPoints': 0,
                    'Players': []
                }
            },
            'Spectators' : [],
            'Map' : mapName,
            'Match Date': matchDate
        }

        # get the csv data
        reader = csv.DictReader(f)
        for row in reader:
            player = parsePlayerData(row, armorPlayerOverrides)
            
            if player['Side'] == 'Spectators':
                matchResults['Spectators'].append(player)
            else:
                side = matchResults[player['Side']]
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
        matchResults['Axis']['Total']['KDR'] = calculateKDR(matchResults['Axis']['Total']['Kills'], matchResults['Axis']['Total']['Deaths'])
        matchResults['Axis']['Infantry']['KDR'] = calculateKDR(matchResults['Axis']['Infantry']['Kills'], matchResults['Axis']['Infantry']['Deaths'])
        matchResults['Axis']['Artillery']['KDR'] = calculateKDR(matchResults['Axis']['Artillery']['Kills'], matchResults['Axis']['Artillery']['Deaths'])
        matchResults['Axis']['Armor']['KDR'] = calculateKDR(matchResults['Axis']['Armor']['Kills'], matchResults['Axis']['Armor']['Deaths'])
        matchResults['Axis']['Unknown']['KDR'] = calculateKDR(matchResults['Axis']['Unknown']['Kills'], matchResults['Axis']['Unknown']['Deaths'])
        matchResults['Allies']['Total']['KDR'] = calculateKDR(matchResults['Allies']['Total']['Kills'], matchResults['Allies']['Total']['Deaths'])
        matchResults['Allies']['Infantry']['KDR'] = calculateKDR(matchResults['Allies']['Infantry']['Kills'], matchResults['Allies']['Infantry']['Deaths'])
        matchResults['Allies']['Artillery']['KDR'] = calculateKDR(matchResults['Allies']['Artillery']['Kills'], matchResults['Allies']['Artillery']['Deaths'])
        matchResults['Allies']['Armor']['KDR'] = calculateKDR(matchResults['Allies']['Armor']['Kills'], matchResults['Allies']['Armor']['Deaths'])
        matchResults['Allies']['Unknown']['KDR'] = calculateKDR(matchResults['Allies']['Unknown']['Kills'], matchResults['Allies']['Unknown']['Deaths'])

        # return results
        return matchResults

# -- Execution Starts Here --

# Iterate through the passed files, parsing each one into a pandas DataFrame
for filePath in sys.argv[1:]:
    name = os.path.basename(filePath)
    print('file:',filePath)
    print(name)
    try:
        results[name] = parseStatsFile(filePath)
    except Exception as e:
        print(type(e).__name__, "–", e)
        os.system('pause')
        pass

# Write the detailed results to a json file
with open(f'matchAnalysisResults_{time.time()}.json', 'w') as f:
    try:
        results['unknownWeapons'] = list(results['unknownWeapons']) # convert set to list because set can't be JSON serialized
        json.dump(results, f)
    except Exception as e:
        print(type(e).__name__, "–", e)
        os.system('pause')
        pass
        
os.system('pause')
