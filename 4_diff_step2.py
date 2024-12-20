import sys
from pathlib import Path

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
OUT_DIR = MAIN_DIR / "out"

if len(sys.argv) != 2:
    print("Usage: python check_step1_execution.py <target_subject>")
    sys.exit(1)

TARGET_SUBJECT = sys.argv[1]

SUBJECT_OUT_DIR = OUT_DIR / TARGET_SUBJECT
USABLE_DIR = SUBJECT_OUT_DIR / "usable_buggy_versions"
PREREQUISITE_DIR = SUBJECT_OUT_DIR / "prerequisite_data"

usable_buggy_versions = []
for version_dir in USABLE_DIR.iterdir():
    usable_buggy_versions.append(version_dir.name)
print(f"Usable buggy versions: {len(usable_buggy_versions)}")

prerequisite_versions = []
for version_dir in PREREQUISITE_DIR.iterdir():
    prerequisite_versions.append(version_dir.name)
print(f"Prerequisite versions: {len(prerequisite_versions)}")

missing_versions = []
for version in usable_buggy_versions:
    if version not in prerequisite_versions:
        missing_versions.append(version)
print(f"Missing versions: {len(missing_versions)}")



LOG_DIR = MAIN_DIR / "log"
SUBJECTT_LOG_DIR = LOG_DIR / TARGET_SUBJECT / "stage03"
missing_versions_machine_core = {}

for version in missing_versions:
    for log_file in SUBJECTT_LOG_DIR.iterdir():
        with open(log_file, "r") as f:
            info = log_file.name.split(".")
            machine = info[0]
            core = info[1]

            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if version in line:
                    if machine not in missing_versions_machine_core:
                        missing_versions_machine_core[machine] = {}
                    if core not in missing_versions_machine_core[machine]:
                        missing_versions_machine_core[machine][core] = []
                    missing_versions_machine_core[machine][core].append(version)
                    break

idx = 1
for machine in missing_versions_machine_core:
    for core in missing_versions_machine_core[machine]:
        print(f"{idx} {machine} {core}: {missing_versions_machine_core[machine][core]}")
        idx += 1