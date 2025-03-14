from pathlib import Path
import os
import subprocess

CURR_FILE = Path(__file__).resolve()
MAIN_DIR = CURR_FILE.parent
BUILD_DIR = MAIN_DIR / "build"
TESTRUNNER = BUILD_DIR / "gtest_zlib"
assert TESTRUNNER.exists(), f"File not found: {TESTRUNNER}"


TC_DB_INIT_CSV = MAIN_DIR / "tc_db_init.csv"
TESTCASES_INIT_DIR = MAIN_DIR / "testcases_init"
os.makedirs(TESTCASES_INIT_DIR, exist_ok=True)


def main():
    # execute jsoncpp_test --list-tests
    result = subprocess.run([str(TESTRUNNER), "--gtest_list_tests"], capture_output=True, text=True, cwd=str(BUILD_DIR))
    if result.returncode != 0:
        raise RuntimeError(f"jsoncpp_test failed with return code {result.returncode}")

    # get line by line from stdout
    test_schemas = {}
    tc_cnt = 0
    first = ""
    second = ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.endswith("."):
            first = line
            continue
        elif line.startswith("Running main() from"):
            continue
        else:
            second = line
            if "# GetParam()" in line:
                second = line.split("#")[0].strip()
            scheme = first + second

            tc_cnt += 1
            tc_id = f"TC{tc_cnt}.sh"
            test_schemas[tc_id] = scheme
    
    # write to tc_db_init.csv and mk executable script
    with open(TC_DB_INIT_CSV, "w") as f:
        f.write("tc_id,schema\n")

        for tc_id, schema in test_schemas.items():
            f.write(f"{tc_id},{schema}\n")
            with open(TESTCASES_INIT_DIR / tc_id, "w") as tc_f:
                tc_f.write("cd ../build/\n")
                tc_f.write(f"./gtest_zlib --gtest_filter={schema}\n")
            os.chmod(TESTCASES_INIT_DIR / tc_id, 0o755)



if __name__ == "__main__":
    main()