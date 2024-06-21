import csv

from lib.utils import *
from analysis.individual import Individual

class Validate:
    def __init__(
            self, subject_name, set_name
        ):
        self.subject_name = subject_name
        self.set_name = set_name

        self.set_dir = out_dir / self.subject_name / self.set_name

        self.individual_list = get_dirs_in_dir(self.set_dir)
    
    def validate_usable_buggy_versions(self):
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating usable buggy versions for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that bug_info.csv exists
            bug_info = individual.individual_dir / 'bug_info.csv'
            assert bug_info.exists(), f"Bug info file {bug_info} does not exist"

            # GET: bug info
            target_code_file, mutant_code_file, buggy_lineno = self.get_bug_info(bug_info)

            # VALIDATE: Assert that testsuite_info/failing_tcs.txt and testsuite_info/passing_tcs.txt exist
            failing_tcs = individual.individual_dir / 'testsuite_info' / 'failing_tcs.txt'
            assert failing_tcs.exists(), f"Failing test cases file {failing_tcs} does not exist"
            passing_tcs = individual.individual_dir / 'testsuite_info' / 'passing_tcs.txt'
            assert passing_tcs.exists(), f"Passing test cases file {passing_tcs} does not exist"

            # VALIDATE: Assert individual.name and buggy_code_file/<individual.name> exist
            buggy_code_file = individual.individual_dir / 'buggy_code_file' / f"{individual_name}"
            assert buggy_code_file.exists(), f"Buggy code file {buggy_code_file} does not exist"

    def validate_prerequisite_data(self):
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating prerequisite data for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that bug_info.csv exists
            bug_info = individual.individual_dir / 'bug_info.csv'
            assert bug_info.exists(), f"Bug info file {bug_info} does not exist"

            # GET: bug info
            target_code_file, mutant_code_file, buggy_lineno = self.get_bug_info(bug_info)

            # VALIDATE: Assert that buggy_line_key.txt exists and that it matches with buggy_lineno
            buggy_line_key_file = individual.individual_dir / 'buggy_line_key.txt'
            assert buggy_line_key_file.exists(), f"Buggy line key file {buggy_line_key_file} does not exist"
            buggy_line_key = self.check_buggy_lineno(buggy_line_key_file, buggy_lineno)

            # VALIDATE: Assert that coverage_summary.csv exists
            coverage_summary = individual.individual_dir / 'coverage_summary.csv'
            assert coverage_summary.exists(), f"Coverage summary file {coverage_summary} does not exist"

            individual.set_tcs()

            # VALIDATE: Assert that coverage_info/postprocessed_coverage.csv exists
            postprocessed_coverage = individual.individual_dir / 'coverage_info' / 'postprocessed_coverage.csv'
            assert postprocessed_coverage.exists(), f"Postprocessed coverage file {postprocessed_coverage} does not exist"

            # VALIDATE: Assert that failing TCs execute the buggy line in postprocessed_coverage.csv
            res = self.check_failing_tcs(postprocessed_coverage, individual.failing_tcs_list, buggy_line_key)
            assert res, f"Failing test cases do not execute the buggy line in {postprocessed_coverage}"

            # VALIDATE: Assert that coverage_info/lines_executed_by_failing_tc.json exists
            lines_executed_by_failing_tc = individual.individual_dir / 'coverage_info' / 'lines_executed_by_failing_tc.json'
            assert lines_executed_by_failing_tc.exists(), f"Lines executed by failing test cases file {lines_executed_by_failing_tc} does not exist"
            lines_executed_by_passing_tc = individual.individual_dir / 'coverage_info' / 'lines_executed_by_passing_tc.json'
            assert lines_executed_by_passing_tc.exists(), f"Lines executed by passing test cases file {lines_executed_by_passing_tc} does not exist"

            # VALIDATE: Assert that line2function_info/line2function.json exists
            line2function_info = individual.individual_dir / 'line2function_info' / 'line2function.json'
            assert line2function_info.exists(), f"Line to function mapping file {line2function_info} does not exist"
        
        print(f"All {len(self.individual_list)} individuals have been validated successfully")
    
    def check_failing_tcs(self, postprocessed_coverage, failing_tc_list, buggy_line_key):
        with open(postprocessed_coverage, 'r') as f:
            reader = csv.DictReader(f)
    
            for row in reader:
                if row['key'] == buggy_line_key:
                    for failing_tc in failing_tc_list:
                        tc_name = failing_tc.split('.')[0]
                        if row[tc_name] == '0':
                            return False
                    return True

    def get_bug_info(self, bug_info_csv):
        with open(bug_info_csv, "r") as f:
            lines = f.readlines()
            target_code_file, mutant_code_file, buggy_lineno = lines[1].strip().split(",")
        
        return target_code_file, mutant_code_file, buggy_lineno
    
    def check_buggy_lineno(self, buggy_line_key_file, buggy_lineno):
        with open(buggy_line_key_file, "r") as f:
            lines = f.readlines()
            buggy_line_key = lines[0].strip()
        
        file_buggy_lineno = buggy_line_key.split("#")[-1]
        
        assert file_buggy_lineno == buggy_lineno, f"Buggy line key {buggy_line_key} does not match with buggy line number {buggy_lineno}"
        return buggy_line_key

    def validate_mbfl_features(self):
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating MBFL features for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that mbfl_featuers.csv exists
            mbfl_features_csv_file = individual.individual_dir / "mbfl_features.csv"
            assert mbfl_features_csv_file.exists(), f"MBFL features file {mbfl_features_csv_file} does not exist"

            # VALIDATE: Assert that there is only one buggy line
            self.check_one_buggy_line(mbfl_features_csv_file)

            # VALIDATE: Assert that selected_mutants.csv exists
            selected_mutants_csv_file = individual.individual_dir / "selected_mutants.csv"
            assert selected_mutants_csv_file.exists(), f"Selected mutants file {selected_mutants_csv_file} does not exist"

            # VALIDATE: Assert that mutation_testing_results.csv exists
            mutation_testing_results_csv_file = individual.individual_dir / "mutation_testing_results.csv"
            assert mutation_testing_results_csv_file.exists(), f"Mutation testing results file {mutation_testing_results_csv_file} does not exist"
        
        print(f"All {len(self.individual_list)} individuals have been validated successfully")
    
    def check_one_buggy_line(self, mbfl_features_csv_file):
        with open(mbfl_features_csv_file, "r") as f:
            reader = csv.DictReader(f)
            buggy_line_cnt = 0
            for row in reader:
                bug_stat = int(row["bug"])
                if bug_stat == 1:
                    buggy_line_cnt += 1
            assert buggy_line_cnt == 1, f"More than one buggy line in {mbfl_features_csv_file}"

    def validate_sbfl_features(self):
        for individual in self.individual_list:
            # VALIDATE: Assert that sbfl_features.csv exists
            sbfl_features_csv_file = individual / "sbfl_features.csv"
            assert sbfl_features_csv_file.exists(), f"SBFL features file {sbfl_features_csv_file} does not exist"
        
        print(f"All {len(self.individual_list)} individuals have been validated successfully")
