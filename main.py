from tkinter import filedialog
import tkinter as tk
import os
import json
import time
from stats_parser import StatsParser
from version import __version__


def open_file_explorer(path):
    if os.name == 'nt':  # For Windows
        os.startfile(path)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(('open', path))
    else:
        print(f"Unable to open file explorer for this operating system: {os.name}")

def main():
    print(f"Welcome to the Hell Let Loose Stats Parser version {__version__}!")
    print("This project was started by -TL- Grekker and has been updated by -TL- JACK.")
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

    directory = os.path.dirname(file_path)
    
    try:
        parsed_results = StatsParser.parse_stats_file(file_path)
        print(f"Successfully parsed {os.path.basename(file_path)}")

        output_file = os.path.join(directory, f'matchAnalysisResults_{int(time.time())}.json')
        with open(output_file, 'w') as f:
            json.dump(parsed_results, f, indent=2)
        print(f"\nResults have been saved to {output_file}")

        open_file_explorer(directory)

    except Exception as e:
        print(f"Error parsing {file_path}: {type(e).__name__} - {e}")

    print("\nThank you for using the Hell Let Loose Stats Parser!")
    print("The file explorer has been opened to the location of the parsed file.")
    print("The program will now close.")

if __name__ == "__main__":
    main()
