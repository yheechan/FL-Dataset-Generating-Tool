from pathlib import Path
from pathlib import Path
import subprocess as sp


jsoncpp_test_exe = Path("src/test_lib_json/jsoncpp_test").resolve()

current_script_path = Path(__file__).resolve()
jsoncpp_dir = current_script_path.parent

testcases_dir = jsoncpp_dir / "testcases"
testcases_dir.mkdir(exist_ok=True)

def make_testcases():
    cmd = [jsoncpp_test_exe, "--list-tests"]
    process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, encoding="utf-8")

    csv_file = "jsoncpp_tc_lists.csv"
    csv_fp = open(csv_file, "w")
    csv_fp.write("TC_id,TC_schema\n")

    tc_cnt = 1
    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        line = line.strip()
        if line == "":
            continue

        tc_file = testcases_dir / f"TC{tc_cnt}.sh"
        with open(tc_file, "w") as tc:
            mv_dir_str = "cd ../src/test_lib_json"
            exec_str = f"timeout 1s ./jsoncpp_test --test {line}"

            tc.write(f"{mv_dir_str}\n")
            tc.write(f"{exec_str}\n")

            # write to csv
            csv_fp.write(f"TC{tc_cnt},{line}\n")

        # change +x permission
        tc_file.chmod(0o777)
        tc_cnt += 1


if __name__ == "__main__":
    make_testcases()
