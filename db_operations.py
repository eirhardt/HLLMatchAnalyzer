import os
import json
import sqlite3
from datetime import datetime

# Define paths
base_folder = os.getcwd()
parsed_csvs_folder = os.path.join(base_folder, "parsed_jsons")
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
            AverageKills REAL DEFAULT 0,
            TotalDeaths INTEGER DEFAULT 0,
            AverageDeaths REAL DEFAULT 0,
            TotalMatches INTEGER DEFAULT 0,
            TotalCombatEffectiveness INTEGER DEFAULT 0,
            AverageCombatEffectiveness REAL DEFAULT 0
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
            PlayerName TEXT,
            TeamID INTEGER,
            Side TEXT,
            PlayerGroup TEXT,
            Kills INTEGER,
            Deaths INTEGER,
            CombatEffectiveness INTEGER,
            FOREIGN KEY (ResultID) REFERENCES ParsedResults (ResultID),
            FOREIGN KEY (PlayerID) REFERENCES Players (PlayerID),
            FOREIGN KEY (TeamID) REFERENCES Teams (TeamID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PlayerTeamAffiliations (
            AffiliationID INTEGER PRIMARY KEY AUTOINCREMENT,
            PlayerID TEXT,
            TeamID INTEGER,
            FirstSeen TEXT,
            LastSeen TEXT,
            MatchesPlayed INTEGER DEFAULT 1,
            FOREIGN KEY (PlayerID) REFERENCES Players (PlayerID),
            FOREIGN KEY (TeamID) REFERENCES Teams (TeamID),
            UNIQUE(PlayerID, TeamID)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PlayerNameHistory (
            NameHistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            PlayerID TEXT,
            PlayerName TEXT,
            FirstSeen TEXT,
            LastSeen TEXT,
            FOREIGN KEY (PlayerID) REFERENCES Players (PlayerID)
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_player_team_affiliation 
        ON PlayerTeamAffiliations (PlayerID, TeamID)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_team_players 
        ON PlayerTeamAffiliations (TeamID)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_name_history_player 
        ON PlayerNameHistory (PlayerID)
    ''')
    
    # Create views
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS TeamPlayers AS
        WITH LatestTeam AS (
            SELECT DISTINCT
                PlayerID,
                TeamID,
                FirstSeen,
                LastSeen,
                MatchesPlayed
            FROM PlayerTeamAffiliations pta
            WHERE (PlayerID, LastSeen) IN (
                SELECT PlayerID, MAX(LastSeen)
                FROM PlayerTeamAffiliations
                GROUP BY PlayerID
            )
        ),
        LatestName AS (
            SELECT DISTINCT
                PlayerID,
                PlayerName
            FROM PlayerNameHistory pnh
            WHERE (PlayerID, LastSeen) IN (
                SELECT PlayerID, MAX(LastSeen)
                FROM PlayerNameHistory
                GROUP BY PlayerID
            )
        )
        SELECT DISTINCT
            p.PlayerID,
            ln.PlayerName as CurrentName,
            t.TeamName,
            p.TotalMatches,
            p.TotalKills,
            p.TotalDeaths,
            p.AverageKills,
            p.AverageDeaths,
            p.AverageCombatEffectiveness,
            lt.FirstSeen as JoinedTeam,
            lt.LastSeen as LastPlayed,
            lt.MatchesPlayed as MatchesWithTeam
        FROM Players p
        JOIN LatestTeam lt ON p.PlayerID = lt.PlayerID
        JOIN Teams t ON lt.TeamID = t.TeamID
        JOIN LatestName ln ON p.PlayerID = ln.PlayerID
        GROUP BY p.PlayerID
    ''')
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS PlayerHistory AS
        SELECT 
            pnh.PlayerName,
            p.PlayerID,
            t.TeamName,
            pta.FirstSeen as JoinedTeam,
            pta.LastSeen as LastPlayed,
            pta.MatchesPlayed
        FROM PlayerTeamAffiliations pta
        JOIN Teams t ON pta.TeamID = t.TeamID
        JOIN Players p ON pta.PlayerID = p.PlayerID
        JOIN PlayerNameHistory pnh ON p.PlayerID = pnh.PlayerID
        WHERE (pnh.PlayerID, pnh.LastSeen) IN (
            SELECT PlayerID, MAX(LastSeen)
            FROM PlayerNameHistory
            GROUP BY PlayerID
        )
        ORDER BY pta.LastSeen DESC
    ''')
    
    conn.commit()

def insert_or_update_team(conn, team_name):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO Teams (TeamName) VALUES (?)', (team_name,))
    cursor.execute('SELECT TeamID FROM Teams WHERE TeamName = ?', (team_name,))
    return cursor.fetchone()[0]

def update_player_name_history(conn, player_id: str, player_name: str):
    """Update the player's name history."""
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get the player's most recent name
    cursor.execute('''
        SELECT PlayerName, NameHistoryID
        FROM PlayerNameHistory
        WHERE PlayerID = ?
        ORDER BY LastSeen DESC
        LIMIT 1
    ''', (player_id,))
    
    last_record = cursor.fetchone()
    
    if last_record is None:
        # First time we've seen this player
        cursor.execute('''
            INSERT INTO PlayerNameHistory (PlayerID, PlayerName, FirstSeen, LastSeen)
            VALUES (?, ?, ?, ?)
        ''', (player_id, player_name, current_date, current_date))
    elif last_record[0] != player_name:
        # Player has changed their name
        cursor.execute('''
            INSERT INTO PlayerNameHistory (PlayerID, PlayerName, FirstSeen, LastSeen)
            VALUES (?, ?, ?, ?)
        ''', (player_id, player_name, current_date, current_date))
    else:
        # Update LastSeen for the current name
        cursor.execute('''
            UPDATE PlayerNameHistory
            SET LastSeen = ?
            WHERE NameHistoryID = ?
        ''', (current_date, last_record[1]))


def insert_or_update_player(conn, player_data):
    """Updated to include name history tracking."""
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO Players (PlayerID, PlayerName, TotalKills, TotalDeaths, TotalMatches, TotalCombatEffectiveness)
        VALUES (?, ?, 0, 0, 0, 0)
    ''', (player_data['PlayerID'], player_data['Name']))
    
    cursor.execute('''
        UPDATE Players SET
        TotalKills = TotalKills + ?,
        TotalDeaths = TotalDeaths + ?,
        TotalMatches = TotalMatches + 1,
        TotalCombatEffectiveness = TotalCombatEffectiveness + ?,
        AverageKills = ROUND(CAST((TotalKills + ?) AS REAL) / (TotalMatches + 1), 1),
        AverageDeaths = ROUND(CAST((TotalDeaths + ?) AS REAL) / (TotalMatches + 1), 1),
        AverageCombatEffectiveness = ROUND(CAST((TotalCombatEffectiveness + ?) AS REAL) / (TotalMatches + 1), 1)
        WHERE PlayerID = ?
    ''', (
        player_data['Kills'],
        player_data['Deaths'],
        player_data['CombatEffectiveness'],
        player_data['Kills'],
        player_data['Deaths'],
        player_data['CombatEffectiveness'],
        player_data['PlayerID']
    ))
    
    # Update name history
    update_player_name_history(conn, player_data['PlayerID'], player_data['Name'])


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
    
    # First insert the match performance as before
    cursor.execute('''
        INSERT INTO MatchPerformance (
            ResultID, PlayerID, PlayerName, TeamID, Side, PlayerGroup, Kills, Deaths, CombatEffectiveness
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        result_id,
        player_data['PlayerID'],
        player_data['Name'],
        team_id,
        player_data['Side'],
        player_data['Group'],
        player_data['Kills'],
        player_data['Deaths'],
        player_data['CombatEffectiveness']
    ))
    
    # Then update the player team affiliation
    if team_id is not None:  # Only track affiliations for actual team members (not spectators)
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Try to update existing affiliation or create new one
        cursor.execute('''
            INSERT INTO PlayerTeamAffiliations (PlayerID, TeamID, FirstSeen, LastSeen, MatchesPlayed)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(PlayerID, TeamID) DO UPDATE SET
                LastSeen = ?,
                MatchesPlayed = MatchesPlayed + 1
            WHERE PlayerID = ? AND TeamID = ?
        ''', (
            player_data['PlayerID'],
            team_id,
            current_date,
            current_date,
            current_date,
            player_data['PlayerID'],
            team_id
        ))

def get_processed_files(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT FileName FROM ParsedResults')
    return set(row[0] for row in cursor.fetchall())

def get_player_team_history(conn, player_id):
    """Get the team history for a specific player."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            t.TeamName,
            pta.FirstSeen,
            pta.LastSeen,
            pta.MatchesPlayed
        FROM PlayerTeamAffiliations pta
        JOIN Teams t ON pta.TeamID = t.TeamID
        WHERE pta.PlayerID = ?
        ORDER BY pta.LastSeen DESC
    ''', (player_id,))
    return cursor.fetchall()

def get_team_roster(conn, team_id):
    """Get the current roster for a specific team."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            p.PlayerName,
            pta.FirstSeen,
            pta.LastSeen,
            pta.MatchesPlayed,
            p.AverageKills,
            p.AverageCombatEffectiveness
        FROM PlayerTeamAffiliations pta
        JOIN Players p ON pta.PlayerID = p.PlayerID
        WHERE pta.TeamID = ?
        ORDER BY pta.MatchesPlayed DESC
    ''', (team_id,))
    return cursor.fetchall()

def process_json_file(conn, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
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