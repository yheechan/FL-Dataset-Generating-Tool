from lib.utils import *

class Individual:
    def __init__(self, subject_name, set_name, individual_name):
        self.subject_name = subject_name
        self.set_name = set_name
        self.name = individual_name

        self.individual_dir = out_dir / self.subject_name / self.set_name / self.name
        assert self.individual_dir.exists(), f"Individual directory {self.individual_dir} does not exist"

        self.testsuite_info_dir = self.individual_dir / "testsuite_info"
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
        