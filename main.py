from tkinter import filedialog
import tkinter as tk
import os
import json
import time
from generate_comparison_graph import create_comprehensive_comparison
from player_data import PlayerData
from stats_parser import StatsParser
from typing import Any
from version import __version__

class UnicodeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerData):
            return obj.to_dict()
        return super().default(obj)
    

def open_file_explorer(path):
    if os.name == 'nt':  # For Windows
        os.startfile(path)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(('open', path))
    else:
        print(f"Unable to open file explorer for this operating system: {os.name}")

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

    directory: str = os.path.dirname(file_path)
    
    try:
        parsed_results: dict[str, Any] = StatsParser.parse_stats_file(file_path)
        print(f"Successfully parsed {os.path.basename(file_path)}")

        output_file: str = os.path.join(directory, f'matchAnalysisResults_{int(time.time())}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, cls=UnicodeJsonEncoder, ensure_ascii=False, indent=4)

        print(f"\nResults have been saved to {output_file}")
        
        graph_file = create_comprehensive_comparison(parsed_results, directory)
        print(f"Comprehensive comparison graph has been saved as '{os.path.basename(graph_file)}'")

        open_file_explorer(directory)

    except Exception as e:
        print(f"Error parsing {file_path}: {type(e).__name__} - {e}")

    print("\nThank you for using the Hell Let Loose Stats Parser!")
    print("The file explorer has been opened to the location of the parsed file.")
    print("The program will now close.")

if __name__ == "__main__":
    main()
