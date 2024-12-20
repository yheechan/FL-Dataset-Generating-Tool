
from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) < 2:
    print(f"Usage: python {CURR_FILE} TARGET_NAME")
    sys.exit(1)

TARGET_NAME = sys.argv[1]

OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
usable_buggy_versinos = OUT_DIR / "usable_buggy_versions"


import subprocess
import random


# Divide versions within usable_buggy_versions into 4 partitions
# and save it within usable_buggy_versions_v<n> where n is 1, 2, 3, 4
usable_buggy_v1 = OUT_DIR / "usable_buggy_versions_v1"
usable_buggy_v2 = OUT_DIR / "usable_buggy_versions_v2"
usable_buggy_v3 = OUT_DIR / "usable_buggy_versions_v3"
usable_buggy_v4 = OUT_DIR / "usable_buggy_versions_v4"

subprocess.run(["mkdir", "-p", usable_buggy_v1])
subprocess.run(["mkdir", "-p", usable_buggy_v2])
subprocess.run(["mkdir", "-p", usable_buggy_v3])
subprocess.run(["mkdir", "-p", usable_buggy_v4])

versions = list(usable_buggy_versinos.iterdir())
random.shuffle(versions)

n = len(versions)
n1 = n // 4
n2 = n1 * 2
n3 = n1 * 3

for i, version_dir in enumerate(versions):
    if i < n1:
        subprocess.run(["cp", "-r", version_dir, usable_buggy_v1])
    elif i < n2:
        subprocess.run(["cp", "-r", version_dir, usable_buggy_v2])
    elif i < n3:
        subprocess.run(["cp", "-r", version_dir, usable_buggy_v3])
    else:
        subprocess.run(["cp", "-r", version_dir, usable_buggy_v4])

    print(f"Copy {version_dir} to usable_buggy_versions_v<n>")




