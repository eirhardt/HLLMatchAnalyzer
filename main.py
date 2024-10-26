import os
import json
import time
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
from generate_comparison_graph import create_comprehensive_comparison
from player_data import PlayerData
from stats_parser import StatsParser
from typing import Any
from version import __version__
from db_operations import process_new_json_files
from datetime import datetime

class UnicodeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerData):
            return obj.to_dict()
        return super().default(obj)

def ensure_parsed_jsons_folder(base_directory: str) -> str:
    parsed_jsons_folder = Path(base_directory) / "parsed_jsons"
    parsed_jsons_folder.mkdir(exist_ok=True)
    return str(parsed_jsons_folder)

def generate_descriptive_filename(parsed_results: dict[str, Any]) -> str:
    team1_name = parsed_results['Axis']['Team Name']
    team2_name = parsed_results['Allies']['Team Name']
    map_name = parsed_results['Map']
    match_date = parsed_results['Match Date']
    processed_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Replace any characters that might not be suitable for filenames
    team1_name = ''.join(c if c.isalnum() else '_' for c in team1_name)
    team2_name = ''.join(c if c.isalnum() else '_' for c in team2_name)
    map_name = ''.join(c if c.isalnum() else '_' for c in map_name)
    match_date = ''.join(c if c.isalnum() else '_' for c in match_date)
    
    return f"{team1_name}_vs_{team2_name}_{map_name}_{match_date}_Processed_{processed_date}.json"

def parse_new_match() -> bool:
    """Parse a new match CSV file into JSON. Returns True if file was parsed successfully."""
    root = tk.Tk()
    root.withdraw()

    file_path: str = filedialog.askopenfilename(
        title="Select CSV file to parse",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not file_path:
        print("No file selected. Skipping CSV parsing.")
        return False

    base_directory: str = os.path.dirname(os.path.abspath(__file__))
    parsed_jsons_folder: str = ensure_parsed_jsons_folder(base_directory)
    
    try:
        parsed_results: dict[str, Any] = StatsParser.parse_stats_file(file_path)
        print(f"Successfully parsed {os.path.basename(file_path)}")

        descriptive_filename = generate_descriptive_filename(parsed_results)
        output_file: str = os.path.join(parsed_jsons_folder, descriptive_filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, cls=UnicodeJsonEncoder, ensure_ascii=False, indent=4)

        print(f"\nResults have been saved to {output_file}")
        
        # Generate comparison graph
        try:
            graph_file = create_comprehensive_comparison(parsed_results, parsed_jsons_folder)
            print(f"Comprehensive comparison graph has been saved as '{os.path.basename(graph_file)}'")
        except Exception as e:
            print(f"Warning: Could not generate comparison graph: {type(e).__name__} - {e}")
            print("Continuing with database operations...")

        return True

    except Exception as e:
        print(f"Error parsing {file_path}: {type(e).__name__} - {e}")
        return False

def main() -> None:
    print(f"Welcome to the Hell Let Loose Stats Parser version {__version__}!")
    print("This project was started by -TL- Grekker and has been updated by -TL- JVCK.")
    
    while True:
        print("\nPlease select an operation:")
        print("1. Parse new CSV file")
        print("2. Update database from all JSON files")
        print("3. Do both")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            parse_new_match()
        elif choice == "2":
            print("\nUpdating database with all parsed match data...")
            process_new_json_files()
            print("Database update complete.")
        elif choice == "3":
            if parse_new_match():
                print("\nUpdating database with all parsed match data...")
                process_new_json_files()
                print("Database update complete.")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

    print("\nThank you for using the Hell Let Loose Stats Parser!")

if __name__ == "__main__":
    main()