from pathlib import Path
import os
import subprocess
import time

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
BUILD_DIR = MAIN_DIR / "build"
TESTRUNNER = BUILD_DIR / "gtest_zlib"
assert TESTRUNNER.exists(), f"File not found: {TESTRUNNER}"

TC_DB_CSV = MAIN_DIR / "tc_db.csv"
TESTCASES_DIR = MAIN_DIR / "testcases"

def run_test(tc_script):
    result = subprocess.run(
        str(tc_script), shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        cwd=TESTCASES_DIR
    )
    return result

def main():
    # get line by line from stdout
    pass_tcs = []
    fail_tcs = []
    tcs_time = []

    with open(TC_DB_CSV, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:
            info = line.strip().split(",")
            tc_id = info[0]

            start_time = time.time()
            result = run_test(TESTCASES_DIR / tc_id)
            end_time = time.time()

            if result.returncode == 0:
                pass_tcs.append(tc_id)
            else:
                fail_tcs.append(tc_id)
            
            exec_time = end_time - start_time
            tcs_time.append(exec_time)

    print(f"pass_tcs: {len(pass_tcs)}")
    print(f"fail_tcs: {len(fail_tcs)}")

    print(f"total time taken: {sum(tcs_time)}")
    print(f"average time taken: {sum(tcs_time)/len(tcs_time)}")


if __name__ == "__main__":
    main()