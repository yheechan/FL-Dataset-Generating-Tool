import sys
from pathlib import Path

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
LOG_DIR = MAIN_DIR / "log"

if len(sys.argv) != 2:
    print("Usage: python check_step1_execution.py <target_subject>")
    sys.exit(1)

TARGET_SUBJECT = sys.argv[1]

SUBJECT_DIR = LOG_DIR / TARGET_SUBJECT
STAGE1_DIR = SUBJECT_DIR / "stage01"

total = 0
machine2core2saves = {}
for file in STAGE1_DIR.iterdir():
    filename = file.name
    info = filename.split(".")
    machine = info[0]
    core = info[1]
    if machine not in machine2core2saves:
        machine2core2saves[machine] = {}
    if core not in machine2core2saves[machine]:
        machine2core2saves[machine][core] = 0
    
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if "- Failing test cases:" in line:
                machine2core2saves[machine][core] += 1
                total += 1

import json
print(json.dumps(machine2core2saves, indent=2))
print(f"Total: {total}")