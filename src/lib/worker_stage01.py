import subprocess as sp

from lib.utils import *
from lib.worker_base import Worker

class WorkerStage01(Worker):
    def __init__(self, subject_name, machine, core, mutant_path, target_file_path, need_configure, verbose=False):
        super().__init__(subject_name, "stage01", "collecting_mutants", machine, core, verbose)
        
        self.test_suite = self.get_testsuite()
        self.assigned_works_dir = self.core_dir / f"stage01-assigned_works"
        self.need_configure = need_configure

        self.assigned_mutant_code_file = self.assigned_works_dir / mutant_path
        assert self.assigned_mutant_code_file.exists(), f"Mutant code file does not exist: {self.assigned_mutant_code_file}"

        self.target_file_path = target_file_path
        self.target_file_code_file = self.core_dir / self.target_file_path
        assert self.target_file_code_file.exists(), f"Target file code file does not exist: {self.target_file_code_file}"

        self.buggy_mutants_dir = out_dir / f"{self.name}" / "buggy_mutants"
        self.buggy_mutants_dir.mkdir(exist_ok=True, parents=True)
    
    def run(self):
        print(f"Testing mutant {self.assigned_mutant_code_file.name} on {self.machine}::{self.core}")
        # 1. Configure subject
        if self.need_configure:
            self.configure_no_cov()

        # 2. Build subject
        self.build()
        self.set_env()

        # 3. Test mutant
        self.test_mutant()
        self.clean_build()
    
    def test_mutant(self):
        # 1. Make patch file
        patch_file = self.make_patch_file(self.target_file_code_file, self.assigned_mutant_code_file, "mutant.patch")

        # 2. Apply patch
        self.apply_patch(self.target_file_code_file, self.assigned_mutant_code_file, patch_file, False)

        # 3. Build the subject, if build fails, skip the mutant
        res = self.build()
        if res != 0:
            print(f"Failed to build on {self.assigned_mutant_code_file.name}")
            self.apply_patch(self.target_file_code_file, self.assigned_mutant_code_file, patch_file, True)
            return
        
        # 4. run the test suite
        self.passing_tcs, self.failing_tcs = self.run_test_suite()
        if self.passing_tcs == [-1] and self.failing_tcs == [-1]:
            print(f"Crash detected on {self.assigned_mutant_code_file.name}")
            self.apply_patch(self.target_file_code_file, self.assigned_mutant_code_file, patch_file, True)
            return

        # 5. Don't save the mutant if all test cases pass
        if len(self.failing_tcs) == 0:
            print(f"Mutant {self.assigned_mutant_code_file.name} is not killed")
            self.apply_patch(self.target_file_code_file, self.assigned_mutant_code_file, patch_file, True)
            return
        
        # 6. Save the mutant if any test case fails
        self.save_mutant()

        # 7. Apply patch reverse
        self.apply_patch(self.target_file_code_file, self.assigned_mutant_code_file, patch_file, True)
    

    def save_mutant(self):
        print(f">> Saving buggy mutant {self.assigned_mutant_code_file.name}")
        buggy_mutant_dir = self.buggy_mutants_dir / self.assigned_mutant_code_file.name
        print_command(["mkdir", "-p", buggy_mutant_dir], self.verbose)
        buggy_mutant_dir.mkdir(parents=True, exist_ok=True)
        
        failing_tcs_file = buggy_mutant_dir / "failing_tcs.txt"
        with failing_tcs_file.open("w") as f:
            content = "\n".join(self.failing_tcs)
            f.write(content)
        
        passing_tcs_file = buggy_mutant_dir / "passing_tcs.txt"
        with passing_tcs_file.open("w") as f:
            content = "\n".join(self.passing_tcs)
            f.write(content)
        
        bug_info_csv = buggy_mutant_dir / "bug_info.csv"
        with bug_info_csv.open("w") as f:
            f.write(f"target_code_file,mutant_code_file\n") 
            f.write(f"{self.target_file_path},{self.assigned_mutant_code_file.name}")

        print(f">> Saved buggy mutant {self.assigned_mutant_code_file.name}")
        print(f"\t - Failing test cases: {len(self.failing_tcs)}")
        print(f"\t - Passing test cases: {len(self.passing_tcs)}")

    
    def run_test_suite(self):
        passing_tcs = []
        failing_tcs = []
        for tc_script in self.test_suite:
            res = self.run_test_case(tc_script)
            if res in crash_codes:
                return [-1], [-1]
            elif res == 0:
                passing_tcs.append(tc_script)
            else:
                failing_tcs.append(tc_script)
        return passing_tcs, failing_tcs
    
    def get_testsuite(self):
        test_suite = []
        for tc_script in self.testsuite_dir.iterdir():
            test_suite.append(tc_script.name)
        test_suite = sorted(test_suite, key=sort_testcase_script_name)
        return test_suite
    
    def print_testsuite(self):
        print(f"Test suite size: {len(self.test_suite)}")
        for idx, tc_script in enumerate(self.test_suite):
            print(f"\t{idx+1}. {tc_script}")
