
from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent


if len(sys.argv) != 3:
    print("Usage: python 6_check_file_cnt_stage01.py <TARGET_NAME> <TARGET_DIR>")
    sys.exit(1)

TARGET_NAME = sys.argv[1]
TARGET_DIR = sys.argv[2]

OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
BUGGY_MUTANTS_DIR = OUT_DIR / TARGET_DIR


file2version = {}
for version_dir in BUGGY_MUTANTS_DIR.iterdir():
    filename = version_dir.name

    info = filename.split(".")
    src_file = info[0]
    version_name = info[1]

    if src_file not in file2version:
        file2version[src_file] = []
    file2version[src_file].append(version_name)


for src_file in file2version:
    print(f"{src_file}: {len(file2version[src_file])}")

print(f"Total: {len(file2version)}")


SUBJECTS_DIR = MAIN_DIR / "subjects" / TARGET_NAME
CONFIG_FILE = SUBJECTS_DIR / "configurations.json"
import json

needed_src_files = []
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)
    for src_file in config["target_files"]:
        name = src_file.split("/")[-1].split(".")[0]
        needed_src_files.append(name)

print(f"Needed: {len(needed_src_files)}")

missing_files = []
print("Missing files:")
for src_file in needed_src_files:
    if src_file not in file2version:
        missing_files.append(src_file)
        print(src_file)

