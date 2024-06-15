#!/usr/bin/python3

from pathlib import Path

test_list = Path("runtest_tc_lists.csv")

library_path = Path("./libs").resolve().__str__()


def make_testcases():
    testcases_dir = Path("testcases")
    testcases_dir.mkdir(exist_ok=True)

    with open(test_list, "r") as f:
        lines = f.readlines()

        for line in lines[1:]:
            line = line.strip()
            info = line.split(",")
            tc_name = info[0]

            tc_file = testcases_dir / f"{tc_name}.sh"
            with open(tc_file, "w") as tc:
                mv_dir_str = "cd ../"
                export_str = f"export LD_LIBRARY_PATH=\"{library_path}:$LD_LIBRARY_PATH\""
                exec_str = f"./.libs/runtest -quiet --single-tc {tc_name}"

                tc.write(f"{mv_dir_str}\n")
                tc.write(f"{export_str}\n")
                tc.write(f"{exec_str}\n")
            
            # change +x permission
            tc_file.chmod(0o777)


if __name__ == "__main__":
    make_testcases()