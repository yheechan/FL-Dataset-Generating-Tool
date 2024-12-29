from pathlib import Path
import json

from lib.database import CRUD


curr_file = Path(__file__).resolve()
curr_dir = curr_file.parent
main_dir = curr_dir.parent
config_dir = main_dir / "configs"
config_json = config_dir / "config.json"

config_fp = config_json.open("r")
config = json.load(config_fp)
config_fp.close()


host = config["database"]["host"]
port = config["database"]["port"]
user = config["database"]["user"]
password = config["database"]["password"]
database = config["database"]["database"]



db = CRUD(host, port, user, password, database)

res = db.read(
    "bug_info",
    columns="bug_idx, mbfl, buggy_line_idx, buggy_file, sbfl",
    conditions={
        "experiment_name": "TF_bot30",
        "prerequisites": True
    }
)

print(f"Total: {len(res)}")

perfile_include_idx = {}
included_bug_idx = []
included_versions = []
past_tested_line_idx = {}
for row in res:
    bug_idx, mbfl, buggy_line_idx, buggy_file, sbfl = row

    if mbfl == True:
        if buggy_file not in past_tested_line_idx:
            past_tested_line_idx[buggy_file] = []
        if buggy_line_idx not in past_tested_line_idx[buggy_file]:
            print(f"MBFL: {bug_idx}")
            past_tested_line_idx[buggy_file].append(buggy_line_idx)
        continue

    if sbfl == False:
        print(f"SBFL: {bug_idx}")
        continue

    if buggy_file in past_tested_line_idx and buggy_line_idx in past_tested_line_idx[buggy_file]:
        continue

    if buggy_file not in perfile_include_idx:
        perfile_include_idx[buggy_file] = []
    
    if buggy_line_idx not in perfile_include_idx[buggy_file]:
        perfile_include_idx[buggy_file].append(buggy_line_idx)
    else:
        print(f"Duplicate: {bug_idx} : {buggy_file} : {buggy_line_idx}")

print(f"Total: {len(perfile_include_idx)}")
total = 0
for file, lines in perfile_include_idx.items():
    print(f"{file}: {len(lines)}")
    total += len(lines)
print(f"Total: {total}")