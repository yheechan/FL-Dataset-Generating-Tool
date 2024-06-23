from lib.utils import *

class Individual:
    def __init__(self, subject_name, set_name, individual_name):
        self.subject_name = subject_name
        self.set_name = set_name
        self.name = individual_name

        self.dir_path = out_dir / self.subject_name / self.set_name / self.name
        assert self.dir_path.exists(), f"Individual directory {self.dir_path} does not exist"

        self.testsuite_info_dir = self.dir_path / "testsuite_info"
        self.testsuite_info_dir.mkdir(exist_ok=True, parents=True)

        self.failing_tcs_file = self.testsuite_info_dir / "failing_tcs.txt"
        self.passing_tcs_file = self.testsuite_info_dir / "passing_tcs.txt"
        self.excluded_failing_tcs_file = self.testsuite_info_dir / "excluded_failing_tcs.txt"
        self.excluded_passing_tcs_file = self.testsuite_info_dir / "excluded_passing_tcs.txt"
        self.ccts_file = self.testsuite_info_dir / "ccts.txt"

        self.set_tcs()
    
    def set_tcs(self):
        self.failing_tcs_list = get_tc_list(self.failing_tcs_file)
        self.passing_tcs_list = get_tc_list(self.passing_tcs_file)
        self.excluded_failing_tcs_list = get_tc_list(self.excluded_failing_tcs_file)
        self.excluded_passing_tcs_list = get_tc_list(self.excluded_passing_tcs_file)
        self.ccts_list = get_tc_list(self.ccts_file)
        self.total_tcs_list = self.failing_tcs_list + self.passing_tcs_list + self.excluded_failing_tcs_list + self.excluded_passing_tcs_list + self.ccts_list

        self.failing_tcs_set = set(self.failing_tcs_list)
        self.passing_tcs_set = set(self.passing_tcs_list)
        self.excluded_failing_tcs_set = set(self.excluded_failing_tcs_list)
        self.excluded_passing_tcs_set = set(self.excluded_passing_tcs_list)
        self.ccts_set = set(self.ccts_list)
        self.total_tcs_set = set(self.total_tcs_list)
    
    def get_bug_info(self):
        bug_info_csv = self.dir_path / "bug_info.csv"

        with open(bug_info_csv, "r") as f:
            lines = f.readlines()
            target_code_file, bug_code_filename, buggy_lineno = lines[1].strip().split(",")
        
        return target_code_file, bug_code_filename, buggy_lineno
