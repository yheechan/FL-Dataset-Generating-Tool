# rm -rf log/$1
# rm -rf out/$1
# rm -rf statistics/$1
# rm -rf timer/$1/*
# rm -rf work/$1

from pathlib import Path
import sys

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent

if len(sys.argv) < 2:
    print(f"Usage: python {CURR_FILE} TARGET_NAME")
    sys.exit(1)

TARGET_NAME = sys.argv[1]

LOG_DIR = MAIN_DIR / "log" / TARGET_NAME
OUT_DIR = MAIN_DIR / "out" / TARGET_NAME
STATISTICS_DIR = MAIN_DIR / "statistics" / TARGET_NAME
TIMER_DIR = MAIN_DIR / "timer" / TARGET_NAME
WORK_DIR = MAIN_DIR / "work" / TARGET_NAME



import subprocess

subprocess.check_call(["rm", "-rf", str(LOG_DIR)])
subprocess.check_call(["rm", "-rf", str(OUT_DIR)])
subprocess.check_call(["rm", "-rf", str(STATISTICS_DIR)])
subprocess.check_call(["rm", "-rf", str(TIMER_DIR)])
subprocess.check_call(["mkdir", "-p", str(TIMER_DIR)])
subprocess.check_call(["rm", "-rf", str(WORK_DIR)])
