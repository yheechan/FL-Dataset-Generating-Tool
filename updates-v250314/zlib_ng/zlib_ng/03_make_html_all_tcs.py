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

HTML_COV_DIR = MAIN_DIR / "html_cov"
HTML_COV_DIR.mkdir(exist_ok=True)


def main():
    object_dir = MAIN_DIR / "build/CMakeFiles/zlibstatic.dir/"
    root_dir = MAIN_DIR

    gcovr_command = [
        "/usr/bin/gcovr",
        "--root", str(root_dir),
        "--object-directory", str(object_dir),
        "--html-details",
        "-o", str(HTML_COV_DIR / "coverage.html"),
        "--gcov-ignore-parse",
        "--gcov-ignore-errors=no_working_dir_found"
    ]

    result = subprocess.run(
        gcovr_command,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        print(result.stdout)
        raise RuntimeError(f"gcovr failed with return code {result.returncode}")
    
    print("gcovr success")


if __name__ == "__main__":
    main()