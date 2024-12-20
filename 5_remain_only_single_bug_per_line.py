
from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) < 2:
    print(f"Usage: python {CURR_FILE} TARGET_NAME")
    sys.exit(1)

TARGET_NAME = sys.argv[1]

OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
PREREQUISITE_DIR = OUT_DIR / "prerequisite_data"


file2line2count = {}
for version_dir in PREREQUISITE_DIR.iterdir():
    filename = version_dir.name

    info = filename.split(".")
    src_file = info[0]
    version_name = info[1]

    bug_info_csv = version_dir / "bug_info.csv"
    with open(bug_info_csv, "r") as f:
        lines = f.readlines()
        info = lines[1].strip().split(",")
        line_no = int(info[-1])

        if src_file not in file2line2count:
            file2line2count[src_file] = {}
        if line_no not in file2line2count[src_file]:
            file2line2count[src_file][line_no] = 0

        file2line2count[src_file][line_no] += 1

line_file_cnt = 0
for src_file in file2line2count:
    for line_no in file2line2count[src_file]:
        line_file_cnt += 1
        print(f"{src_file}:{line_no}")
        print(f"Count: {file2line2count[src_file][line_no]}")
        print()

print(f"Total: {line_file_cnt}")

    
