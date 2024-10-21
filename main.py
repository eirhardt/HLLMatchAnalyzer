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
from db_operations import process_new_json_files  # Import the database operation function

class UnicodeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerData):
            return obj.to_dict()
        return super().default(obj)

def open_file_explorer(path):
    if os.name == 'nt':  # For Windows
        os.startfile(path)
    elif os.name == 'posix':  # For macOS and Linux
        import subprocess
        subprocess.call(('open', path))
    else:
        print(f"Unable to open file explorer for this operating system: {os.name}")

def ensure_parsed_jsons_folder(base_directory: str) -> str:
    parsed_jsons_folder = Path(base_directory) / "parsed_jsons"
    parsed_jsons_folder.mkdir(exist_ok=True)
    return str(parsed_jsons_folder)

def main() -> None:
    print(f"Welcome to the Hell Let Loose Stats Parser version {__version__}!")
    print("This project was started by -TL- Grekker and has been updated by -TL- JVCK.")
    print("This script will parse CSV files produced by CRCON after a Hell Let Loose match.")

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    print("\nPlease select the CSV file you want to parse.")
    file_path: str = filedialog.askopenfilename(
        title="Select CSV file to parse",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not file_path:  # User cancelled the file dialog
        print("No file selected. Exiting.")
        return

    # Get the base directory (where the script is located)
    base_directory: str = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the parsed_jsons folder exists
    parsed_jsons_folder: str = ensure_parsed_jsons_folder(base_directory)
    
    try:
        parsed_results: dict[str, Any] = StatsParser.parse_stats_file(file_path)
        print(f"Successfully parsed {os.path.basename(file_path)}")

        output_file: str = os.path.join(parsed_jsons_folder, f'matchAnalysisResults_{int(time.time())}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, cls=UnicodeJsonEncoder, ensure_ascii=False, indent=4)

        print(f"\nResults have been saved to {output_file}")
        
        graph_file = create_comprehensive_comparison(parsed_results, parsed_jsons_folder)
        print(f"Comprehensive comparison graph has been saved as '{os.path.basename(graph_file)}'")

        # Run database operations
        print("\nUpdating database with new match data...")
        process_new_json_files()
        print("Database update complete.")

        open_file_explorer(parsed_jsons_folder)

    except Exception as e:
        print(f"Error parsing {file_path}: {type(e).__name__} - {e}")

    print("\nThank you for using the Hell Let Loose Stats Parser!")
    print("The file explorer has been opened to the location of the parsed file.")
    print("The program will now close.")

if __name__ == "__main__":
    main()