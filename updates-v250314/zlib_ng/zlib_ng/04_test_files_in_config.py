from pathlib import Path
import os
import subprocess
import time
import json

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
BUILD_DIR = MAIN_DIR / "build"
config_file = MAIN_DIR / "configurations.json"


def main():
    with open(config_file, "r") as f:
        config = json.load(f)

        target_files = config["target_files"]
        target_preprocessed_files = config["target_preprocessed_files"]

        not_existing_target_files = []
        not_existing_target_preprocessed_files = []
        for file in target_files:
            file_str = "/".join(file.split("/")[1:])
            file_path = MAIN_DIR / file_str
            if not file_path.exists():
                not_existing_target_files.append(file_path)
        
        for file in target_preprocessed_files:
            file_str = "/".join(file.split("/")[1:])
            file_path = MAIN_DIR / file_str
            if not file_path.exists():
                not_existing_target_preprocessed_files.append(file_path)
        
    for file in not_existing_target_files:
        print(f"File not found: {file}")
    
    for file in not_existing_target_preprocessed_files:
        print(f"File not found: {file}")
            


if __name__ == "__main__":
    main()