
from pathlib import Path

curr_file = Path(__file__).resolve()
curr_dir = curr_file.parent

target_file = curr_dir / "TC834.raw.json"

import json

with open(target_file, "r") as f:
    data = json.load(f)
    for file in data["files"]:
        filename = file["file"]
        if "reduce_layer.cpp" not in filename: continue

        for line in file["lines"]:
            line_number = line["line_number"]
            print(f"Line number: {line_number}")

        print(filename)

