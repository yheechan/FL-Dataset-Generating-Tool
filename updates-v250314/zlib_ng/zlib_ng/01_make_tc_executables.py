from pathlib import Path
import os
import subprocess
import time

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
BUILD_DIR = MAIN_DIR / "build"
TESTRUNNER = BUILD_DIR / "gtest_zlib"
assert TESTRUNNER.exists(), f"File not found: {TESTRUNNER}"


TC_DB_INIT_CSV = MAIN_DIR / "tc_db_init.csv"
TESTCASES_INIT_DIR = MAIN_DIR / "testcases_init"

TC_DB_CSV = MAIN_DIR / "tc_db.csv"
TESTCASES_DIR = MAIN_DIR / "testcases"
TESTCASES_DIR.mkdir(exist_ok=True)

def run_test(tc_script):
    result = subprocess.run(
        str(tc_script), shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        cwd=TESTCASES_INIT_DIR
    )
    return result

def main():
    # get line by line from stdout
    pass_tcs = []
    fail_tcs = []
    tcs_time = []

    db_fp = open(TC_DB_CSV, "w")
    db_fp.write("tc_id,schema,time_taken\n")

    new_tc_cnt = 0
    with open(TC_DB_INIT_CSV, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:
            info = line.strip().split(",")
            tc_id = info[0]
            schema = info[1]

            start_time = time.time()
            result = run_test(TESTCASES_INIT_DIR / tc_id)
            end_time = time.time()


            if "SKIPPED" in result.stdout.splitlines()[-1]:
                continue
            if result.returncode == 0:
                pass_tcs.append(tc_id)
            else:
                fail_tcs.append(tc_id)
            
            exec_time = end_time - start_time
            tcs_time.append(exec_time)

            new_tc_cnt += 1
            new_tc_id = f"TC{new_tc_cnt}.sh"
            db_fp.write(f"{new_tc_id},{schema},{exec_time}\n")

            target_time = int(exec_time) + 2
            with open(TESTCASES_DIR / new_tc_id, "w") as tc_f:
                tc_f.write("cd ../build/\n")
                tc_f.write(f"timeout {target_time}s ./gtest_zlib --gtest_filter={schema}\n")
            os.chmod(TESTCASES_DIR / new_tc_id, 0o755)

    db_fp.close()
    print(f"pass_tcs: {len(pass_tcs)}")
    print(f"fail_tcs: {len(fail_tcs)}")

    print(f"total time taken: {sum(tcs_time)}")
    print(f"average time taken: {sum(tcs_time)/len(tcs_time)}")


if __name__ == "__main__":
    main()