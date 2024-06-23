from copy import deepcopy
import random
import subprocess as sp
import csv

from lib.utils import *
from analysis.individual import Individual
from lib.experiment import Experiment
from analysis.rank_utils import *
from analysis.reconstruct_utils import *
        

class Reconstruct:
    def __init__(
            self, subject_name, set_name,
        ):
        self.subject_name = subject_name
        
        self.set_name = set_name
        self.set_dir = out_dir / self.subject_name / self.set_name
        self.individual_list = get_dirs_in_dir(self.set_dir)
        self.set_size = len(self.individual_list)

        self.stat_dir = stats_dir / self.subject_name
        if not self.stat_dir.exists():
            self.stat_dir.mkdir(parents=True, exist_ok=True)
    
    def reduce_testsuite_size(self, reduced_size):
        failing_tcs_set = set()
        passing_tcs_set = set()
        total_testsuite_set = set()
        keep_set = set()

        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Analyzing {individual_name} for reducing test suite")

            individual = Individual(self.subject_name, self.set_name, individual_name)

            keep = 0
            if "issue" in individual_name:
                keep = 1
            
            failing_tcs_set.update(individual.failing_tcs_list)
            passing_tcs_set.update(individual.passing_tcs_list)

            if keep == 1:
                keep_set.update(individual.failing_tcs_list)

            total_testsuite_set.update(individual.failing_tcs_list)
            total_testsuite_set.update(individual.passing_tcs_list)

        # ==============================================================

        # remove tcs in passing_set that exists in failing_set
        passing_tcs_set = passing_tcs_set - failing_tcs_set
        failing_tcs_set = failing_tcs_set - keep_set

        # reduced test suite
        excluded_tc_list = []
        failing_tcs_list = list(failing_tcs_set)
        passing_tcs_list = list(passing_tcs_set)

        # 1. save tcs to keep
        reduced_test_suite = []
        keep_tcs_list = list(keep_set)
        reduced_test_suite = deepcopy(keep_tcs_list)

        # 2. randomly select tcs to keep
        random.shuffle(failing_tcs_list)
        random.shuffle(passing_tcs_list)

        # 3. select tcs the amount of reduced_size
        while len(reduced_test_suite) < reduced_size:
            if len(failing_tcs_list) > 0:
                tc = failing_tcs_list.pop()
                reduced_test_suite.append(tc)
            elif len(passing_tcs_list) > 0:
                tc = passing_tcs_list.pop()
                reduced_test_suite.append(tc)
        
        # 4. get excluded tcs
        excluded_tc_list = failing_tcs_list + passing_tcs_list

        # 5. save reduced test suite
        reduced_testsuite_file = self.stat_dir / "reduced_test_suite.txt"
        with open(reduced_testsuite_file, "w") as f:
            reduced_tcs_list = sorted(reduced_test_suite, key=sort_testcase_script_name)
            content = "\n".join(reduced_tcs_list)
            f.write(content)
        
        # 6. save excluded tcs
        excluded_tcs_file = self.stat_dir / "excluded_tcs.txt"
        with open(excluded_tcs_file, "w") as f:
            excluded_tcs_list = sorted(excluded_tc_list, key=sort_testcase_script_name)
            content = "\n".join(excluded_tcs_list)
            f.write(content)
        

        # ==============================================================

        reduced_tc_set = set()
        with open(reduced_testsuite_file, "r") as f:
            for line in f:
                reduced_tc_set.add(line.strip())
        
        included_individual_cnt = 0
        excluded_individual_cnt = 0

        reduced_individuals_dir = out_dir / self.subject_name / f"{self.set_name}-reduced"
        reduced_individuals_dir.mkdir(exist_ok=True, parents=True)

        # 1. reduce test suite of each individual
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Reducing test suite of {individual_name}")

            individual = Individual(self.subject_name, self.set_name, individual_name)

            # 2. overwrite failing and passing tcs
            reduced_failing_tcs_set = set(individual.failing_tcs_list).intersection(reduced_tc_set)
            reduced_passing_tcs_set = set(individual.passing_tcs_list).intersection(reduced_tc_set)

            excluded_failing_tcs_set = set(individual.failing_tcs_list) - reduced_tc_set
            excluded_failing_tcs_list = list(excluded_failing_tcs_set)
            excluded_failing_tcs_list = sorted(excluded_failing_tcs_list, key=sort_testcase_script_name)
            excluded_passing_tcs_set = set(individual.passing_tcs_list) - reduced_tc_set
            excluded_passing_tcs_list = list(excluded_passing_tcs_set)
            excluded_passing_tcs_list = sorted(excluded_passing_tcs_list, key=sort_testcase_script_name)

            reduced_failing_tcs_list = list(reduced_failing_tcs_set)
            reduced_passing_tcs_list = list(reduced_passing_tcs_set)
            reduced_failing_tcs_list = sorted(reduced_failing_tcs_list, key=sort_testcase_script_name)
            reduced_passing_tcs_list = sorted(reduced_passing_tcs_list, key=sort_testcase_script_name)

            # 3. save excluded tcs
            if len(reduced_failing_tcs_list) == 0 or len(reduced_passing_tcs_list) == 0:
                excluded_individual_cnt += 1
                continue

            included_individual_cnt += 1
            sp.check_call(["cp", "-r", individual.dir_path, reduced_individuals_dir])

            reduced_dir_path = reduced_individuals_dir / individual_name
            assert reduced_dir_path.exists(), f"Reduced individual directory {reduced_dir_path} does not exist"

            new_testsuite_dir = reduced_dir_path / "testsuite_info"
            assert new_testsuite_dir.exists(), f"New test suite directory {new_testsuite_dir} does not exist"

            new_failing_tcs = new_testsuite_dir / "failing_tcs.txt"
            new_passing_tcs = new_testsuite_dir / "passing_tcs.txt"
            new_excluded_failing_tcs = new_testsuite_dir / "excluded_failing_tcs.txt"
            new_excluded_passing_tcs = new_testsuite_dir / "excluded_passing_tcs.txt"

            with open(new_failing_tcs, "w") as f:
                content = "\n".join(reduced_failing_tcs_list)
                f.write(content)

            with open(new_passing_tcs, "w") as f:
                content = "\n".join(reduced_passing_tcs_list)
                f.write(content)

            with open(new_excluded_failing_tcs, "w") as f:
                content = "\n".join(excluded_failing_tcs_list)
                f.write(content)

            with open(new_excluded_passing_tcs, "w") as f:
                content = "\n".join(excluded_passing_tcs_list)
                f.write(content)


        print(f"\n\n>>>>> REDUCED RESULTS <<<<<")
        print(f"Total # of buggy versions: {len(self.individual_list)}")
        print(f"Total # of reduced tcs: {len(reduced_test_suite)}")
        print(f"# of excluded failing tcs: {len(failing_tcs_list)}")
        print(f"# of excluded passing tcs: {len(passing_tcs_list)}")
        print(f"Total # of excluded tcs: {len(excluded_tc_list)}")


        print(f"\nTotal individual: {len(self.individual_list)}")
        print(f"Total included individual: {included_individual_cnt}")
        print(f"Total excluded individual: {excluded_individual_cnt}")
    
    def appropriate_version_with_all_failing_tcs(self):

        appropiate_individuals_dir = out_dir / self.subject_name / f"{self.set_name}-appropriate"
        appropiate_individuals_dir.mkdir(exist_ok=True, parents=True)

        included_buggy_version_cnt = 0
        excluded_buggy_version_cnt = 0
        for individual in self.individual_list:

            individual = Individual(self.subject_name, self.set_name, individual.name)
            print(f"Analyzing {individual.name} for appropriate versions with all failing TCs")

            failing_tcs_set = set(individual.failing_tcs_list)
            excluded_failing_tc_set = set(individual.excluded_failing_tcs_list)

            total_failing_tcs_set = failing_tcs_set.union(excluded_failing_tc_set)

            if len(total_failing_tcs_set) < 500:
                sp.run(["cp", "-r", individual.dir_path, appropiate_individuals_dir])
                included_buggy_version_cnt += 1
            else:
                excluded_buggy_version_cnt += 1
        
        print(f"Number of buggy versions included: {included_buggy_version_cnt}")
        print(f"Number of buggy versions excluded: {excluded_buggy_version_cnt}")
    
    def remove_versions_mbfl_meeting_criteria(self, criteria):
        self.experiment = Experiment()
        self.max_mutants = self.experiment.experiment_config["max_mutants"]
        self.mutant_keys = get_mutant_keys(self.max_mutants)
        self.criteriaA_versions = []
        self.criteriaB_versions = []

        for idx, version_dir in enumerate(self.individual_list):
            print(f"\n{idx+1}/{len(self.individual_list)}: {version_dir.name}")
            individual = Individual(self.subject_name, self.set_name, version_dir.name)

            mbfl_features_csv_file = individual.dir_path / "mbfl_features.csv"
            assert mbfl_features_csv_file.exists(), f"MBFL features file {mbfl_features_csv_file} does not exist"

            buggy_line_key = get_buggy_line_key_from_data(individual.dir_path)
            lines_executed_by_failing_tcs = get_lines_executed_by_failing_tcs_from_data(individual.dir_path)
            assert buggy_line_key in lines_executed_by_failing_tcs, f"buggy_line_key {buggy_line_key} not in lines_executed_by_failing_tcs"

            mutation_testing_result_data = get_mutation_testing_results_form_data(individual.dir_path, buggy_line_key)

            if "criteriaA" in criteria:
                res = analyze_buggy_line_with_f2p_0(
                    mbfl_features_csv_file,
                    buggy_line_key,
                    self.mutant_keys,
                )

                if res == 0:
                    print(f"\t Criteria A satisfied (f2p of buggy line is 0)")
                    self.criteriaA_versions.append(individual.name)
            if "criteriaB" in criteria:
                res = analyze_non_buggy_line_with_f2p_above_th(
                    mbfl_features_csv_file,
                    buggy_line_key,
                    self.mutant_keys,
                    10
                )

                if res == 1:
                    print(f"\t Criteria B satisfied (# of bad lines > 10)")
            
        print(f"\n\nCriteria A versions: {len(self.criteriaA_versions)}")
        print(f"Criteria B versions: {len(self.criteriaB_versions)}")

        ext_name = "-".join(criteria)
        dir_name = f"{self.set_name}-removed-{ext_name}"
        removed_versions_dir = out_dir / self.subject_name / dir_name
        removed_versions_dir.mkdir(exist_ok=True, parents=True)

        original_set = set([version_dir.name for version_dir in self.individual_list])
        removed_set = set(self.criteriaA_versions).union(set(self.criteriaB_versions))
        remaining_set = original_set - removed_set
        print(f"Total original versions: {len(original_set)}")
        print(f"Total removed versions: {len(removed_set)}")
        print(f"Total remaining versions: {len(remaining_set)}")

        for idx, version_dir in enumerate(self.individual_list):
            if version_dir.name not in removed_set:
                sp.run(["cp", "-r", version_dir, removed_versions_dir])

    
    def combine_mbfl_sbfl(self):
        # Create FL dataset directory
        self.fl_dataset_dir = out_dir / self.subject_name / f"FL-dataset-{self.subject_name}"
        if self.fl_dataset_dir.exists():
            sp.run(f"rm -rf {self.fl_dataset_dir}", shell=True)
        self.fl_dataset_dir.mkdir(parents=True, exist_ok=True)

        # Sort the individual list
        self.individual_list = sorted(self.individual_list)
        for idx, version_dir in enumerate(self.individual_list):
            if "issue" in version_dir.name:
                self.individual_list.insert(0, self.individual_list.pop(idx))
        
        self.experiment = Experiment()
        self.max_mutants = self.experiment.experiment_config["max_mutants"]
        self.mutant_keys = get_mutant_keys(self.max_mutants)

        bug_version_mutation_info = self.fl_dataset_dir / "bug_version_mutation_info.csv"
        bug_version_mutation_info_fp = bug_version_mutation_info.open("w")
        bug_version_mutation_info_fp.write(",,,,,Before Mutation,,,,,After Mutation\n")
        bug_version_mutation_info_fp.write("bug_id,target_file_name,Buggy Code Filename,Mutation Operator,Start Line#,Start Col#,End Line#,End Col#,Target Token,Start Line#,Start Col#,End Line#,End Col#,Mutated Token,Extra Info\n")

        for idx, version_dir in enumerate(self.individual_list):
            print(f"\n{idx+1}/{self.set_size}: {version_dir.name}")
            individual = Individual(self.subject_name, self.set_name, version_dir.name)
            
            bug_id = f"bug{idx+1}"

            bug_info_csv_file = individual.dir_path / "bug_info.csv"
            assert bug_info_csv_file.exists(), f"Bug info file {bug_info_csv_file} does not exist"

            target_code_file, bug_code_filename, buggy_lineno = individual.get_bug_info()
            target_file_name = target_code_file.split("/")[-1]

            # 1. copy buggy_code_file to <fl-dataset-dir>/buggy_code_file_per_bug_version/<bug-id>/<buggy-code-file> as target-file-name
            copy_buggy_code_file(
                bug_id, individual.dir_path,
                bug_code_filename, target_file_name,
                self.fl_dataset_dir
            )


            buggy_line_key_txt = individual.dir_path / "buggy_line_key.txt"
            assert buggy_line_key_txt.exists(), f"Buggy line key file {buggy_line_key_txt} does not exist"

            # 2. copy buggy_line_key.txt to <fl-dataset-dir>/buggy_line_key_per_bug_version/<bug-id>.buggy_line_key.txt
            copy_buggy_line_key_file(
                bug_id, individual.dir_path,
                buggy_line_key_txt,
                self.fl_dataset_dir
            )

            postprocessed_cov_file = individual.dir_path / "coverage_info" / "postprocessed_coverage.csv"
            assert postprocessed_cov_file.exists(), f"Postprocessed coverage file {postprocessed_cov_file} does not exist"

            # 3. copy coverage_info/postprocessed_coverage.csv to <fl-dataset-dir>/postprocessed_coverage_per_bug_version/<bug-id>.cov_data.csv
            copy_postprocessed_coverage_file(
                bug_id, individual.dir_path,
                postprocessed_cov_file,
                self.fl_dataset_dir
            )


            testsuite_info_dir = individual.dir_path / "testsuite_info"

            # 4. copy the contents in testuite_info_dir to <fl-dataset-dir>/test_case_info_per_bug_version/<bug-id>
            copy_test_case_info(
                bug_id, testsuite_info_dir,
                self.fl_dataset_dir
            )

            sbfl_feature_file = individual.dir_path / "sbfl_features.csv"
            mbfl_feature_file = individual.dir_path / "mbfl_features.csv"
            assert sbfl_feature_file.exists(), f"SBFL feature file {sbfl_feature_file} does not exist"
            assert mbfl_feature_file.exists(), f"MBFL feature file {mbfl_feature_file} does not exist"

            combine_sbfl_mbfl_features(
                bug_id, sbfl_feature_file, mbfl_feature_file,
                self.fl_dataset_dir, self.mutant_keys
            )


            mutant_info_csv_file = individual.dir_path / "mutant_info.csv"

            # 5. write <fl-dataset-dir>/bug_version_mutation_info.csv
            write_bug_version_mutation_info(
                bug_id, target_file_name, bug_code_filename,
                self.fl_dataset_dir,
                mutant_info_csv_file, bug_version_mutation_info_fp
            )
        
        bug_version_mutation_info_fp.close()
