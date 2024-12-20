
from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) < 2:
    print(f"Usage: python {CURR_FILE} TARGET_NAME")
    sys.exit(1)

TARGET_NAME = sys.argv[1]

OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
initial_v1 = OUT_DIR / "initial_selected_buggy_versions-v1"
initial = OUT_DIR / "initial_selected_buggy_versions"


import subprocess

for version_dir in initial_v1.iterdir():
    # make a copy of version_dir to inital
    subprocess.run(["cp", "-r", version_dir, initial])
    print(f"Copy {version_dir} to {initial}")



