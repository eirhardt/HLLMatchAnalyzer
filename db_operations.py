import os
import json
import sqlite3
from datetime import datetime

# Define paths
base_folder = os.getcwd()
parsed_csvs_folder = os.path.join(base_folder, "parsed_csvs")
db_path = os.path.join(base_folder, "hell_let_loose.db")

def create_tables(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
            TeamName TEXT UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Players (
            PlayerID TEXT PRIMARY KEY,
            PlayerName TEXT,
            TotalKills INTEGER DEFAULT 0,
            TotalDeaths INTEGER DEFAULT 0,
            TotalMatches INTEGER DEFAULT 0,
            TotalCombatEffectiveness INTEGER DEFAULT 0,
            TotalOffensivePoints INTEGER DEFAULT 0,
            TotalDefensivePoints INTEGER DEFAULT 0,
            TotalSupportPoints INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ParsedResults (
            ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT UNIQUE,
            ParseDate TEXT,
            MapName TEXT,
            MatchDate TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Maps (
            MapID INTEGER PRIMARY KEY AUTOINCREMENT,
            MapName TEXT UNIQUE,
            TimesPlayed INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MatchPerformance (
            MatchPerformanceID INTEGER PRIMARY KEY AUTOINCREMENT,
            ResultID INTEGER,
            PlayerID TEXT,
            TeamID INTEGER,
            Side TEXT,
            PlayerGroup TEXT,
            Kills INTEGER,
            Deaths INTEGER,
            CombatEffectiveness INTEGER,
            OffensivePoints INTEGER,
            DefensivePoints INTEGER,
            SupportPoints INTEGER,
            FOREIGN KEY (ResultID) REFERENCES ParsedResults (ResultID),
            FOREIGN KEY (PlayerID) REFERENCES Players (PlayerID),
            FOREIGN KEY (TeamID) REFERENCES Teams (TeamID)
        )
    ''')
    
    conn.commit()

def insert_or_update_team(conn, team_name):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO Teams (TeamName) VALUES (?)', (team_name,))
    cursor.execute('SELECT TeamID FROM Teams WHERE TeamName = ?', (team_name,))
    return cursor.fetchone()[0]

def insert_or_update_player(conn, player_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO Players (PlayerID, PlayerName)
        VALUES (?, ?)
    ''', (player_data['PlayerID'], player_data['Name']))
    
    cursor.execute('''
        UPDATE Players SET
        TotalKills = TotalKills + ?,
        TotalDeaths = TotalDeaths + ?,
        TotalMatches = TotalMatches + 1,
        TotalCombatEffectiveness = TotalCombatEffectiveness + ?,
        TotalOffensivePoints = TotalOffensivePoints + ?,
        TotalDefensivePoints = TotalDefensivePoints + ?,
        TotalSupportPoints = TotalSupportPoints + ?
        WHERE PlayerID = ?
    ''', (
        player_data['Kills'],
        player_data['Deaths'],
        player_data['CombatEffectiveness'],
        player_data['OffensivePoints'],
        player_data['DefensivePoints'],
        player_data['SupportPoints'],
        player_data['PlayerID']
    ))

def insert_parsed_result(conn, file_name, map_name, match_date):
    cursor = conn.cursor()
    parse_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT OR IGNORE INTO ParsedResults (FileName, ParseDate, MapName, MatchDate)
        VALUES (?, ?, ?, ?)
    ''', (file_name, parse_date, map_name, match_date))
    return cursor.lastrowid

def update_map_stats(conn, map_name):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO Maps (MapName, TimesPlayed)
        VALUES (?, 0)
    ''', (map_name,))
    cursor.execute('''
        UPDATE Maps SET TimesPlayed = TimesPlayed + 1
        WHERE MapName = ?
    ''', (map_name,))

def insert_match_performance(conn, result_id, player_data, team_id):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO MatchPerformance (
            ResultID, PlayerID, TeamID, Side, Group, Kills, Deaths,
            CombatEffectiveness, OffensivePoints, DefensivePoints, SupportPoints
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        result_id,
        player_data['PlayerID'],
        team_id,
        player_data['Side'],
        player_data['Group'],
        player_data['Kills'],
        player_data['Deaths'],
        player_data['CombatEffectiveness'],
        player_data['OffensivePoints'],
        player_data['DefensivePoints'],
        player_data['SupportPoints']
    ))

def process_json_file(conn, file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    file_name = os.path.basename(file_path)
    map_name = data['Map']
    match_date = data['Match Date']
    
    result_id = insert_parsed_result(conn, file_name, map_name, match_date)
    update_map_stats(conn, map_name)
    
    for side in ['Axis', 'Allies']:
        team_name = data[side]['Team Name']
        team_id = insert_or_update_team(conn, team_name)
        
        for group in ['Infantry', 'Artillery', 'Armor']:
            for player_data in data[side][group]['Players']:
                insert_or_update_player(conn, player_data)
                insert_match_performance(conn, result_id, player_data, team_id)
    
    for player_data in data['Spectators']:
        insert_or_update_player(conn, player_data)
        insert_match_performance(conn, result_id, player_data, None)

def get_processed_files(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT FileName FROM ParsedResults')
    return set(row[0] for row in cursor.fetchall())

def process_new_json_files():
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    
    processed_files = get_processed_files(conn)
    
    for filename in os.listdir(parsed_csvs_folder):
        if filename.endswith('.json') and filename not in processed_files:
            file_path = os.path.join(parsed_csvs_folder, filename)
            print(f"Processing new file: {filename}")
            process_json_file(conn, file_path)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    process_new_json_files()