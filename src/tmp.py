from pathlib import Path
import json

"""
a = {"hello": [1, 2, 3], "world": ["fuck", "you"]}
for b in a:
  print(b)
"""

def foo(mydata):
  mydata["hello world"] = [1, 2, 3]


init_data = {}
print(init_data)
foo(init_data)
print(init_data)
exit()


curr_file = Path(__file__).resolve()
curr_dir = curr_file.parent
main_dir = curr_dir.parent
tmp_txt = curr_dir / "tmp.json"

assert tmp_txt.exists()
fp = open(tmp_txt, "r")
data = json.load(fp)

for idx, key in enumerate(data):
  print(idx, key)

"""
db_file = main_dir / "out/jsoncpp_test//generated_mutants/jsoncpp_test-src-lib_json-json_writer.cpp/json_writer_mut_db.csv"
assert db_file.exists(), f"File not found: {db_file}"

import csv

with open(db_file, "r") as f:
    reader = csv.reader(f, escapechar='\\', quotechar='"', delimiter=',')
    next(reader)
    for row in reader:
        mut_name = row[0]
        if mut_name == "json_writer.MUT255.cpp":
            print(row)
        mut_op = row[1]
        pre_start_line = row[2]
        pre_start_col = row[3]
        pre_end_line = row[4]
        pre_end_col = row[5]
        pre_mut = row[6]
        post_start_line = row[7]
        post_start_col = row[8]
        post_end_line = row[9]
        post_end_col = row[10]
        post_mut = row[11]
"""
