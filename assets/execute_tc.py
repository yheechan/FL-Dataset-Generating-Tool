#!/usr/bin/python3

import argparse
from pathlib import Path
import subprocess as sp
import time
import json
import os


# Define constants for paths
curr_file = Path(__file__).resolve()
main_dir = curr_file.parent

testcases_dir = main_dir / "testcases"
ld_dir = main_dir / ".libs"
assert ld_dir.exists(), f"ld_dir directory does not exist: {ld_dir}"

# Update environment with test data path
my_env = os.environ.copy()
if "LD_LIBRARY_PATH" not in my_env:
    my_env["LD_LIBRARY_PATH"] = ld_dir
else:
    my_env["LD_LIBRARY_PATH"] = f"{ld_dir}:{my_env['LD_LIBRARY_PATH']}"



def sort_testcase(tc):
    """
    Sorts test cases by their integer ID.
    """
    return [int(tc[2:].split(".")[0])]


def execute_test_case(testcase_path, env, testcase_dir):
    """
    Executes a single test case shell script and returns the result.
    """
    print(f"Running {testcase_path}")
    return sp.run(
        str(testcase_path), shell=True,
        stderr=sp.PIPE, stdout=sp.PIPE,
        encoding="utf-8", cwd=testcase_dir,
        env=env
    )



def run_tests():
    """
    Main function to run the tests for a specified module.
    """
    # change global obj_dir and root_dir
    global obj_dir, root_dir, module_name, testcases_dir

    tc_list = sorted([tc.name for tc in testcases_dir.iterdir()], key=sort_testcase)
    pass_tcs, fail_tcs = [], []
    exec_times, cov_times = [], []
    special_tcs = []

    for tc_cnt, tc_name in enumerate(tc_list, start=1):
        tc_sh = testcases_dir / tc_name
        assert tc_sh.exists(), f"Testcase file {tc_sh} does not exist"


        # Step 2: Run the test case
        start_time = time.time()
        result = execute_test_case(tc_sh, my_env, testcases_dir)
        exec_time = time.time() - start_time

        if result.returncode == 0:
            print(f"\t{tc_name} PASSED")
            pass_tcs.append(tc_name)
        else:
            if result.returncode != 1:
                special_tcs.append((tc_name, result.returncode))
            print(f"\t{tc_name} FAILED")
            fail_tcs.append(tc_name)


        exec_times.append(exec_time)
        # if tc_cnt == 1:  # Limit to 3 test cases
        #     break

    # Output results
    print(f"Total test cases: {len(tc_list)}")
    print(f"Passed test cases: {len(pass_tcs)}")
    print(f"Failed test cases: {len(fail_tcs)}")
    print(f"Total time taken: {sum(exec_times)}")
    print(f"Average time taken: {sum(exec_times) / len(tc_list)}")
    # print(f"Average coverage time: {sum(cov_times) / len(tc_list)}")

    # Save result to JSON
    result_data = {
        "total_test_cases": len(tc_list),
        "passed_test_cases": len(pass_tcs),
        "passed_test_cases_list": pass_tcs,
        "failed_test_cases": len(fail_tcs),
        "failed_test_cases_list": fail_tcs,
        "total_time_taken": sum(exec_times),
        "average_time_taken": sum(exec_times) / len(tc_list),
        "special_test_cases": special_tcs,
        "special_test_cases_count": len(special_tcs),
        # "coverage_time_list": cov_times,
        # "average_coverage_time": sum(cov_times) / len(tc_list),
    }

    with open(main_dir / f"execute_tc_results.json", "w") as result_fp:
        json.dump(result_data, result_fp, indent=2)


if __name__ == "__main__":
    run_tests()
