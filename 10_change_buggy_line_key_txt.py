
from pathlib import Path
import sys
import csv

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) < 2:
    print(f"Usage: python {CURR_FILE} TARGET_NAME")
    sys.exit(1)

TARGET_NAME = sys.argv[1]

OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
prerequisite_data = OUT_DIR / "prerequisite_data_v1"


not_found = []
for version_dir in prerequisite_data.iterdir():
    found = 0
    print(f"Processing {version_dir}")
    buggy_line_key_txt = version_dir / "buggy_line_key.txt"
    with open(buggy_line_key_txt, "r") as f:
        buggy_line_key = f.read().strip()
    print(f"\tbuggy_line_key: {buggy_line_key}")

    # with open(buggy_line_key_txt, "w") as f:
    target_file, func, num = buggy_line_key.split("#")
    target_File = target_file.split("/")[-1]
    buggy_line_key = f"{target_File}#{func}#{num}"

    pp_cov_file = version_dir / "coverage_info" / "postprocessed_coverage.csv"
    assert pp_cov_file.exists()

    with open(pp_cov_file, "r") as f:
        reader = csv.reader(f)
        # skip header
        next(reader)
        for row in reader:
            row_key = row[0]
            row_target_file, row_func, row_num = row_key.split("#")
            if row_target_file == target_file:
                if row_num == num:
                    found = 1
                    with open(buggy_line_key_txt, "w") as f:
                        f.write(row_key)
                    break
    if not found:
        not_found.append(version_dir)

print("Not found:")
for nf in not_found:
    print(nf)



