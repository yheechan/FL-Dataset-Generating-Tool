import subprocess as sp

from lib.utils import *
from lib.worker_base import Worker

class WorkerStage02(Worker):
    def __init__(self, subject_name, machine, core, version_name, need_configure, verbose=False):
        super().__init__(subject_name, "stage02", "selecting_usable_buggy_mutants", machine, core, verbose)
        
        self.assigned_works_dir = self.core_dir / f"stage02-assigned_works"
        self.need_configure = need_configure

        self.version_dir = self.assigned_works_dir / version_name

        self.target_code_file_path, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_dir)
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {buggy_code_filename}"
    
        self.failing_tcs_list = self.get_tc_list(self.version_dir, "failing_tcs.txt")

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)

        self.cov_dir = self.core_dir / "coverage" / self.version_dir.name
        print_command(["mkdir", "-p", self.cov_dir], self.verbose)
        self.cov_dir.mkdir(exist_ok=True, parents=True)

        self.core_repo_dir = self.core_dir / self.name

        self.set_filtered_files_for_gcovr()

        self.usable_buggy_versions_dir = out_dir / f"{self.name}" / "usable_buggy_versions"
        self.usable_buggy_versions_dir.mkdir(exist_ok=True, parents=True)

    def run(self):
        print(f"Testing version {self.version_dir.name} on {self.machine}::{self.core}")

        # 1. Configure subject
        if self.need_configure:
            self.configure_yes_cov()
        
        # 2. Build subject
        self.build()
        self.set_env()

        # 4. Test version
        self.test_version()
        self.clean_build()
    
    def test_version(self):
        
        # 1. Make patch file
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")

        # 2. Apply patch
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Build the subject, if build fails, skip the version
        res = self.build()
        if res != 0:
            print(f"Failed to build on {self.version_dir.name}")
            self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
            return
        
        # 4. run the test suite
        for tc_script_name in self.failing_tcs_list:
            # 4-1. remove past coverage
            self.remove_all_gcda(self.core_repo_dir)

            # 4-2. Run test case
            res = self.run_test_case(tc_script_name)
            if res == 0:
                print(f"Test case {tc_script_name} passed")
                self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
                return
            
            # 4-3 Remove untarged files for coverage
            self.remove_untargeted_files_for_gcovr(self.core_repo_dir)
            
            # 4-4. Collect coverage
            raw_cov_file = self.generate_coverage_json(
                self.core_repo_dir, self.cov_dir, tc_script_name,
            )

            # 4-5 Check if the buggy line is coveraged
            buggy_line_covered = self.check_buggy_line_covered(
                tc_script_name, raw_cov_file, self.target_code_file_path, self.buggy_lineno
            )
            if buggy_line_covered == 1:
                print(f"Buggy line {self.buggy_lineno} is NOT covered by test case {tc_script_name}")
                self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
                return
            if buggy_line_covered == -2:
                print(f"File {self.target_code_file_path} is not in the coverage")
                self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
                return
            
            print(f"Buggy line {self.buggy_lineno} is covered by test case {tc_script_name}")

        # 5. Save the version
        self.save_version()

        # 6. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
    
    def save_version(self):
        print(f">> Saving version {self.version_dir.name}")
        print_command(["cp", "-r", self.version_dir, self.usable_buggy_versions_dir], self.verbose)
        sp.check_call(["cp", "-r", self.version_dir, self.usable_buggy_versions_dir])
