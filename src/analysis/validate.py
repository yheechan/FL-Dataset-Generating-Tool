import csv

from lib.utils import *
from analysis.rank_utils import *
from lib.susp_score_formula import *
from analysis.individual import Individual

class Validate:
    def __init__(
            self, subject_name, set_name
        ):
        self.subject_name = subject_name
        self.set_name = set_name

        self.set_dir = out_dir / self.subject_name / self.set_name

    # ++++++++++++++++++++++++++++++++++++++++++++
    # ++++ VALIDATE USABLE BUGGY VERSION DATA ++++
    # ++++++++++++++++++++++++++++++++++++++++++++
    def validate_usable_buggy_versions(self):
        self.individual_list = get_dirs_in_dir(self.set_dir)
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating usable buggy versions for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that bug_info.csv exists
            bug_info = individual.dir_path / 'bug_info.csv'
            assert bug_info.exists(), f"Bug info file {bug_info} does not exist"

            # GET: bug info
            target_code_file, bug_code_filename, buggy_lineno = individual.get_bug_info()

            # VALIDATE: Assert that testsuite_info/failing_tcs.txt and testsuite_info/passing_tcs.txt exist
            failing_tcs = individual.dir_path / 'testsuite_info' / 'failing_tcs.txt'
            assert failing_tcs.exists(), f"Failing test cases file {failing_tcs} does not exist"
            passing_tcs = individual.dir_path / 'testsuite_info' / 'passing_tcs.txt'
            assert passing_tcs.exists(), f"Passing test cases file {passing_tcs} does not exist"

            # VALIDATE: Assert individual.name and buggy_code_file/<individual.name> exist
            buggy_code_file = individual.dir_path / 'buggy_code_file' / f"{bug_code_filename}"
            assert buggy_code_file.exists(), f"Buggy code file {buggy_code_file} does not exist"

    # ++++++++++++++++++++++++++++++++++++
    # ++++ VALIDATE PREREQUISITE DATA ++++
    # ++++++++++++++++++++++++++++++++++++
    def validate_prerequisite_data(self):
        self.individual_list = get_dirs_in_dir(self.set_dir)
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating prerequisite data for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that bug_info.csv exists
            bug_info = individual.dir_path / 'bug_info.csv'
            assert bug_info.exists(), f"Bug info file {bug_info} does not exist"

            # GET: bug info
            target_code_file, bug_code_filename, buggy_lineno = individual.get_bug_info()

            # VALIDATE: Assert that buggy_line_key.txt exists and that it matches with buggy_lineno
            buggy_line_key_file = individual.dir_path / 'buggy_line_key.txt'
            assert buggy_line_key_file.exists(), f"Buggy line key file {buggy_line_key_file} does not exist"
            buggy_line_key = self.check_buggy_lineno(buggy_line_key_file, buggy_lineno)

            # VALIDATE: Assert that coverage_summary.csv exists
            coverage_summary = individual.dir_path / 'coverage_summary.csv'
            assert coverage_summary.exists(), f"Coverage summary file {coverage_summary} does not exist"

            individual.set_tcs()

            # VALIDATE: Assert that coverage_info/postprocessed_coverage.csv exists
            postprocessed_coverage = individual.dir_path / 'coverage_info' / 'postprocessed_coverage.csv'
            assert postprocessed_coverage.exists(), f"Postprocessed coverage file {postprocessed_coverage} does not exist"

            postprocessed_coverage_noCCTs = individual.dir_path / 'coverage_info' / 'postprocessed_coverage_noCCTs.csv'
            assert postprocessed_coverage_noCCTs.exists(), f"Postprocessed coverage no CCTs file {postprocessed_coverage_noCCTs} does not exist"

            # VALIDATE: Assert that failing TCs execute the buggy line in postprocessed_coverage.csv
            res = self.check_failing_tcs(postprocessed_coverage, individual.failing_tcs_list, buggy_line_key)
            assert res, f"Failing test cases do not execute the buggy line in {postprocessed_coverage}"

            res = self.check_failing_tcs(postprocessed_coverage_noCCTs, individual.failing_tcs_list, buggy_line_key)
            assert res, f"Failing test cases do not execute the buggy line in {postprocessed_coverage_noCCTs}"

            # VALIDATE: Assert the postprocessed_coverage_noCCTs.csv has no CCTs
            self.check_CCTs(postprocessed_coverage_noCCTs, individual.ccts_list, notExist=True)

            # Validate: Assert the postprocessed_coverage.csv has CCTs
            self.check_CCTs(postprocessed_coverage, individual.ccts_list, notExist=False)

            # VALIDATE: Assert that coverage_info/lines_executed_by_failing_tc.json exists
            lines_executed_by_failing_tc = individual.dir_path / 'coverage_info' / 'lines_executed_by_failing_tc.json'
            assert lines_executed_by_failing_tc.exists(), f"Lines executed by failing test cases file {lines_executed_by_failing_tc} does not exist"
            lines_executed_by_passing_tc = individual.dir_path / 'coverage_info' / 'lines_executed_by_passing_tc.json'
            assert lines_executed_by_passing_tc.exists(), f"Lines executed by passing test cases file {lines_executed_by_passing_tc} does not exist"
            lines_executed_by_ccts = individual.dir_path / 'coverage_info' / 'lines_executed_by_ccts.json'
            assert lines_executed_by_ccts.exists(), f"Lines executed by CCTs file {lines_executed_by_ccts} does not exist"

            # VALIDATE: Assert that line2function_info/line2function.json exists
            line2function_info = individual.dir_path / 'line2function_info' / 'line2function.json'
            assert line2function_info.exists(), f"Line to function mapping file {line2function_info} does not exist"

            # VALIDATE: Assert that len(passing_tcs) > 0 and len(failing_tcs) > 0
            assert len(individual.failing_tcs_list) > 0, f"length of failing tcs list is less than 0"
            assert len(individual.passing_tcs_list) > 0, f"length of failing tcs list is less than 0"
        
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
                    print(f"\t [VAL] Failing test cases execute buggy line check passed in {postprocessed_coverage.name}")
                    return True
    
    def check_buggy_lineno(self, buggy_line_key_file, buggy_lineno):
        with open(buggy_line_key_file, "r") as f:
            lines = f.readlines()
            buggy_line_key = lines[0].strip()
        
        file_buggy_lineno = buggy_line_key.split("#")[-1]
        
        assert file_buggy_lineno == buggy_lineno, f"Buggy line key {buggy_line_key} does not match with buggy line number {buggy_lineno}"
        return buggy_line_key
    
    def check_CCTs(self, coverage_csv, ccts_list, notExist=True):
        with open(coverage_csv, 'r') as f:
            reader = csv.DictReader(f)
    
            for row in reader:
                for cct in ccts_list:
                    cct_name = cct.split(".")[0]
                    if notExist:
                        assert cct_name not in row, f"CCT {cct_name} found in {coverage_csv}"
                    else:
                        assert cct_name in row, f"CCT {cct_name} not found in {coverage_csv}"
        print(f"\t [VAL] CCTs check passed notExist={notExist}")

    # ++++++++++++++++++++++++++++++++
    # ++++ VALIDATE MBFL FEATURES ++++
    # ++++++++++++++++++++++++++++++++
    def validate_mbfl_features(self, trialName=None):
        self.individual_list = get_dirs_in_dir(self.set_dir)
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Validating MBFL features for {individual_name}")
            individual = Individual(self.subject_name, self.set_name, individual_name)

            # VALIDATE: Assert that mbfl_featuers.csv exists
            mbfl_features_csv_file = individual.dir_path / "mbfl_features.csv"
            assert mbfl_features_csv_file.exists(), f"MBFL features file {mbfl_features_csv_file} does not exist"

            # VALIDATE: Assert that there is only one buggy line
            self.check_one_buggy_line(mbfl_features_csv_file)

            # Validate: Assert that mbfl_feature_noCCTs.csv exists
            mbfl_features_noCCTs_csv_file = individual.dir_path / "mbfl_features_noCCTs.csv"
            assert mbfl_features_noCCTs_csv_file.exists(), f"MBFL features no CCTs file {mbfl_features_noCCTs_csv_file} does not exist"

            # VALIDATE: Assert that there is only one buggy line
            self.check_one_buggy_line(mbfl_features_noCCTs_csv_file)

            # VALIDATE: Assert that selected_mutants.csv exists
            if trialName != None:
                selected_mutants_csv_file = individual.dir_path / f"selected_mutants-{trialName}.csv"
                assert selected_mutants_csv_file.exists(), f"Selected mutants file {selected_mutants_csv_file} does not exist"

            # VALIDATE: Assert that mutation_testing_results.csv exists
            if trialName != None:
                mutation_testing_results_csv_file = individual.dir_path / f"mutation_testing_results-{trialName}.csv"
            else:
                mutation_testing_results_csv_file = individual.dir_path / f"mutation_testing_results.csv"
            assert mutation_testing_results_csv_file.exists(), f"Mutation testing results file {mutation_testing_results_csv_file} does not exist"

            # VALIDATE: assert that mutation_testing_results_noCCTs exists
            if trialName != None:
                mutation_testing_results_noCCTs_csv_file = individual.dir_path / f"mutation_testing_results_noCCTs-{trialName}.csv"
            else:
                mutation_testing_results_noCCTs_csv_file = individual.dir_path / f"mutation_testing_results_noCCTs.csv"
            assert mutation_testing_results_noCCTs_csv_file.exists(), f"Mutation testing results no CCTs file {mutation_testing_results_noCCTs_csv_file} does not exist"
        
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

    # ++++++++++++++++++++++++++++++++
    # ++++ VALIDATE SBFL FEATURES ++++
    # ++++++++++++++++++++++++++++++++
    def validate_sbfl_features(self):
        self.individual_list = get_dirs_in_dir(self.set_dir)
        for individual in self.individual_list:
            print(f"Validating SBFL features for {individual.name}")
            
            # VALIDATE: Assert that sbfl_features.csv exists
            sbfl_features_csv_file = individual / "sbfl_features.csv"
            assert sbfl_features_csv_file.exists(), f"SBFL features file {sbfl_features_csv_file} does not exist"

            # VALIDATE: Assert that sbfl_feature_noCCTs.csv exists
            sbfl_features_noCCTs_csv_file = individual / "sbfl_features_noCCTs.csv"
            assert sbfl_features_noCCTs_csv_file.exists(), f"SBFL features no CCTs file {sbfl_features_noCCTs_csv_file} does not exist"

            # VALIDATE: Assert that there is only one buggy line
            self.check_one_buggy_line(sbfl_features_csv_file)
            self.check_one_buggy_line(sbfl_features_noCCTs_csv_file)
        
        print(f"All {len(self.individual_list)} individuals have been validated successfully")


    # ++++++++++++++++++++++++++++++++
    # ++++ VALIDATE FL FEATURES ++++
    # ++++++++++++++++++++++++++++++++
    def validate_fl_features(self):

        bug_version_mutation_info_file = self.set_dir / "bug_version_mutation_info.csv"
        assert bug_version_mutation_info_file.exists(), f"Bug version mutation info file {bug_version_mutation_info_file} does not exist"

        bugs = {}
        with open(bug_version_mutation_info_file, "r") as f:
            lines = f.readlines()
            for line in lines[2:]:
                line = line.strip()
                info = line.split(",")
                bug_id = info[0]
                assert bug_id not in bugs, f"Duplicate bug id {bug_id}"
                bugs[bug_id] = line

        bug_keys = list(bugs.keys())
        bug_keys = sorted(bug_keys, key=sort_bug_id)

        for idx, bug in enumerate(bug_keys):
            print(f"Validating FL features for {bug} ({idx+1}/{len(bugs)})")
            fl_features_file = self.set_dir / f"FL_features_per_bug_version/{bug}.fl_features.csv"
            assert fl_features_file.exists(), f"FL features file {fl_features_file} does not exist"

            # VALIDATE: that there is only one row with "bug" column as 1
            self.check_one_buggy_line(fl_features_file)
            print(f"\t VAL01: One buggy line check passed")




            failing_tcs_file = self.set_dir / f"test_case_info_per_bug_version/{bug}/failing_tcs.txt"
            assert failing_tcs_file.exists(), f"Failing test cases file {failing_tcs_file} does not exist"
            passing_tcs_file = self.set_dir / f"test_case_info_per_bug_version/{bug}/passing_tcs.txt"
            assert passing_tcs_file.exists(), f"Passing test cases file {passing_tcs_file} does not exist"

            failing_tcs_list = get_tc_list(failing_tcs_file)
            passing_tcs_list = get_tc_list(passing_tcs_file)
            num_utilized_tcs = len(failing_tcs_list) + len(passing_tcs_list)

            # VALIDATE: that the ep, ef, np, nf values from fl_features_file (csv) add up to num_utilized_tcs
            self.check_spectrum2num_utilized_tcs(fl_features_file, num_utilized_tcs)
            print(f"\t VAL02: Spectrum to number of utilized test cases check passed")




            buggy_line_key_file = self.set_dir / f"buggy_line_key_per_bug_version/{bug}.buggy_line_key.txt"
            assert buggy_line_key_file.exists(), f"Buggy line key file {buggy_line_key_file} does not exist"

            with open(buggy_line_key_file, "r") as f:
                buggy_line_key = f.readline().strip()
            
            postprocessed_coverage_file = self.set_dir / f"postprocessed_coverage_per_bug_version/{bug}.cov_data.csv"
            assert postprocessed_coverage_file.exists(), f"Postprocessed coverage file {postprocessed_coverage_file} does not exist"

            # VALIDATE: that all failing tcs execute the buggy line
            res = self.check_failing_tcs(postprocessed_coverage_file, failing_tcs_list, buggy_line_key)
            assert res, f"Failing test cases do not execute the buggy line in {postprocessed_coverage_file}"
            print(f"\t VAL03: Failing test cases execute buggy line check passed")




            num_failing_tcs = len(failing_tcs_list)
            fl_features_file_with_susp = self.set_dir / f"FL_features_per_bug_version_with_susp_scores/{bug}.fl_features_with_susp_scores.csv"
            assert fl_features_file_with_susp.exists(), f"FL features file with suspicious scores {fl_features_file_with_susp} does not exist"
            
            # VALIDATE: that with mutation features from fl_features_file,
            # the met and muse score from fl_features_file_with_susp can be derived
            self.check_met_muse(fl_features_file, fl_features_file_with_susp, num_failing_tcs)
            print(f"\t VAL04: MET and MUSE score check passed")


            bug_info = bugs[bug]
            target_code_file_name = self.get_target_code_file_name(bug_info)
            buggy_code_file = self.set_dir / f"buggy_code_file_per_bug_version/{bug}/{target_code_file_name}"
            assert buggy_code_file.exists(), f"Buggy code file {buggy_code_file} does not exist"

            # VALIDATE: that the mutated code exists in the buggy code file
            self.check_mutated_code(buggy_code_file, bug_info, buggy_line_key)
            print(f"\t VAL05: Mutated code check passed")

            # if idx == 7:
            #     break

        print(f"All {len(bugs)} bugs have been validated successfully")
    
    def check_mutated_code(self, buggy_code_file, bug_info, buggy_line_key):
        written_buggy_lineno = int(buggy_line_key.split("#")[-1])

        info = bug_info.split(",")
        bug_id = info[0]
        target_code_file_name = info[1]
        buggy_code_file_name = info[2]
        
        mut_op = info[3]
        if mut_op == "":
            return

        buggy_lineno = int(info[4])
        assert written_buggy_lineno == buggy_lineno, f"Buggy line number {written_buggy_lineno} does not match with buggy line number {buggy_lineno}"

        before_mutation = info[8]
        after_mutation = info[13]
        
        # print(f"bug_id: {bug_id}")
        # print(f"target_code_file_name: {target_code_file_name}")
        # print(f"line_no: {buggy_lineno}")
        # print(f"before_mutation: {before_mutation}")
        # print(f"after_mutation: {after_mutation}")

        with open(buggy_code_file, "r", encoding="utf-8", errors="ignore") as f: # 2024-08-19
            lines = f.readlines()
            buggy_line = lines[buggy_lineno-1].strip()
            assert after_mutation in buggy_line, f"Mutated code {after_mutation} not found in buggy code file {buggy_code_file}"





    
    def get_target_code_file_name(self, bug_info):
        info = bug_info.split(",")
        bug_id = info[0]
        target_code_file_name = info[1]
        return target_code_file_name
    
    def check_met_muse(self, fl_features_file, fl_features_file_with_susp, num_failing_tcs):
        max_mutants = self.get_max_mutants_from_feature_file(fl_features_file)
        mutant_keys = get_mutant_keys_as_pairs(max_mutants)
        tot_failed_TCs, total_p2f, total_f2p = self.measure_required_info(fl_features_file, mutant_keys)

        # score format: key: formula_key, value: score
        scores = {}
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                met_score = measure_metallaxis(row, mutant_keys)
                muse_data = measure_muse(row, total_p2f, total_f2p, mutant_keys)
                muse_score = muse_data[muse_key]
                scores[row["key"]] = {
                    "met": met_score,
                    "muse": muse_score
                }

        with open(fl_features_file_with_susp, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["key"]
                met_score = float(row[met_key])
                muse_score = float(row[muse_key])
                assert scores[key]["met"] == met_score, f"MET score for {key} does not match"
                assert scores[key]["muse"] == muse_score, f"MUSE score for {key} does not match"
    
    def measure_required_info(self, fl_features_file, mutant_keys):
        tot_failed_TCs = self.get_tot_failed_TCs(fl_features_file)

        total_p2f = 0
        total_f2p = 0
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for p2f_m, f2p_m in mutant_keys:
                    if row[p2f_m] == "-1" and row[f2p_m] == "-1":
                        continue
                    p2f = int(row[p2f_m])
                    f2p = int(row[f2p_m])
                    total_p2f += p2f
                    total_f2p += f2p
        
        return tot_failed_TCs, total_p2f, total_f2p
    
    def get_tot_failed_TCs(self, fl_features_file):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                num_failing_tcs = int(row["# of totfailed_TCs"])
                return num_failing_tcs
    
    def get_max_mutants_from_feature_file(self, fl_features_file):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                max_mutants = int(row["# of mutants"])
                return max_mutants
        
    
    def check_spectrum2num_utilized_tcs(self, fl_features_file, num_utilized_tcs):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ep = int(row["ep"])
                ef = int(row["ef"])
                np = int(row["np"])
                nf = int(row["nf"])
                assert ep + ef + np + nf == num_utilized_tcs, f"Sum of ep, ef, np, nf is not equal to {num_utilized_tcs} in {fl_features_file}"
    
