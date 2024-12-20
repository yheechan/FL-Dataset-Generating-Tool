from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) != 4:
    print("Usage: python 2_measuretime.py TARGET_NAME START_FILE END_FILE")
    sys.exit(1)

TARGET_NAME = sys.argv[1]
start_file = sys.argv[2]
end_file = sys.argv[3]

TIMER_DIR = MAIN_DIR / "timer"
TARGET_DIR = TIMER_DIR / TARGET_NAME

start_file = TARGET_DIR / start_file
end_file = TARGET_DIR / end_file


def read_time(file):
    # Sat Dec 14 01:13:54 KST 2024
    with open(file) as f:
        time_str = f.readline().strip()

    from datetime import datetime
    time = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Z %Y")
    return time

def calc_time_duration(start_file, end_file):
    start_time = read_time(start_file)
    end_time = read_time(end_file)
    duration = end_time - start_time
    return duration

duration = calc_time_duration(start_file, end_file)
print(duration)