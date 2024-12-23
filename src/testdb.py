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
res = db.table_exists("test_table")


db.update(
    "test_table",
    set_values={"test": True},
    conditions={"name": "Heechan"}
)


print(res)
res = db.read(
    "test_table",
    columns="*",
    conditions={"name": "Heechan", "test": True},
)

for row in res:
    print(row)
print()

"""
if not db.table_exists("test_table"):
    print("Creating test_table")
    db.create_table("test_table", "name TEXT, age INT")

db.insert("test_table", "name, age", "'Alice', 25")
db.insert("test_table", "name, age", "'Bob', 30")
db.insert("test_table", "name, age", "'Charlie', 35")
db.insert("test_table", "name, age", "'Alice', 23")

res = db.read("test_table")
for row in res:
    print(row)
print()

db.update(
    "test_table",
    {"name": "Heechan"},
    {"age": 35}
)
res = db.read("test_table")
for row in res:
    print(row)
print()

db.delete("test_table", conditions={"name": "Alice"})
res = db.read("test_table")
for row in res:
    print(row)
print()


if not db.column_exists("test_table", "job"):
    db.add_column("test_table", "job TEXT")

db.update(
    "test_table",
    {"job": "Engineer"},
    {"name": "Bob"}
)
db.update(
    "test_table",
    {"job": "Researcher"},
    {"name": "Heechan"}
)
db.insert("test_table", "name, age", "'David', 40")

res = db.read("test_table")
for row in res:
    print(row)
print()

res = db.value_exists("test_table", conditions={"name": "David"})
if res == 1:
    print("David exists")
else:
    print("David does not exist")
res = db.value_exists("test_table", conditions={"name": "Alice"})
if res == 1:
    print("Alice exists")
else:
    print("Alice does not exist")


if not db.column_exists("test_table", "test"):
    db.add_column("test_table", "test BOOLEAN DEFAULT NULL")

res = db.read("test_table")
for row in res:
    print(row)
"""
