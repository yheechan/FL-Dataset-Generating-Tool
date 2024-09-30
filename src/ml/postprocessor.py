import csv
import json
import shutil

from lib.utils import *
from lib.susp_score_formula import *
from analysis.rank_utils import *


class Postprocessor:
    def __init__(
        self, subject_name, dataset_name
    ):
        self.subject_name = subject_name
        self.dataset_name = dataset_name

        self.subject_dir = out_dir / self.subject_name
        self.dataset_dir = self.subject_dir / self.dataset_name

        self.fl_features_dir = self.dataset_dir / "FL_features_per_bug_version"
        self.feature_csv_list = [f for f in self.fl_features_dir.iterdir() if not f.is_dir()]
        self.feature_csv_list = sorted(self.feature_csv_list, key=lambda x: int(x.name.split(".")[0][3:]))
        
        self.pp_fl_features_dir = self.dataset_dir / "PP_FL_features_per_bug_version"
        if self.pp_fl_features_dir.exists():
            shutil.rmtree(self.pp_fl_features_dir)
        self.pp_fl_features_dir.mkdir(exist_ok=True, parents=True)

    def run(self):
        print(">> Postprocessing FL features")
        for feature_csv in self.feature_csv_list:
            print(f"Processing {feature_csv.name}...")

            pp_data = self.process_feature_csv(feature_csv)
            pp_csv = self.pp_fl_features_dir / feature_csv.name
            self.write_pp_data_to_csv(pp_data, pp_csv)
            # break
    
    def process_feature_csv(self, feature_csv):
        bug_id = feature_csv.name.split(".")[0]

        totFailed_cnt, max_mutant_count = self.get_mbfl_prerequisites(feature_csv)
        mutant_key_list = get_mutant_keys_as_pairs(max_mutant_count)
        total_p2f, total_f2p = self.get_total_killed_count(feature_csv, mutant_key_list)
        fail_cnt, pass_cnt = self.get_tc_cnt(bug_id)

        # key: susp scores
        pp_data = {}
        with open(feature_csv, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                tot_failed_TCs_line = int(row["# of totfailed_TCs"])
                assert totFailed_cnt == tot_failed_TCs_line, "Error: totFailed_cnt != tot_failed_TCs_line"

                line_key = row["key"]
                bug_status = int(row["bug"])
                e_p, e_f, n_p, n_f = int(row["ep"]), int(row["ef"]), int(row["np"]), int(row["nf"])

                fl_features = {}
                fl_features["bug"] = bug_status
                for sbfl_formula in pp_sbfl_formulas:
                    sbfl_score = sbfl(
                        e_p, e_f, n_p, n_f,
                        formula=sbfl_formula,
                        fails=fail_cnt, passes=pass_cnt
                    )
                    fl_features[sbfl_formula] = sbfl_score
                

                # MBFL scores
                metallaxis_score = measure_metallaxis(row, mutant_key_list)
                fl_features["metallaxis"] = metallaxis_score

                muse_data = measure_muse(row, total_p2f, total_f2p, mutant_key_list)
                muse_score = muse_data["muse susp. score"]
                fl_features["muse"] = muse_score

                assert line_key not in pp_data, f"Error: {line_key} already exists in pp_data"
                pp_data[line_key] = fl_features
        
        return pp_data


    
    def get_mbfl_prerequisites(self, feature_csv):
        totFailed_cnt = -1
        max_mutant_count = -1

        with open(feature_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                totFailed_cnt = int(row["# of totfailed_TCs"])
                max_mutant_count = int(row["# of mutants"])
                break
        
        assert totFailed_cnt != -1, "Error: totFailed_cnt is not set"
        assert max_mutant_count != -1, "Error: max_mutant_count is not set"
        
        return totFailed_cnt, max_mutant_count

    def get_total_killed_count(self, feature_csv, mutant_key_list):
        total_f2p = 0
        total_p2f = 0

        with open(feature_csv, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                for p2f_m, f2p_m in mutant_key_list:
                    p2f, f2p = return_f2p_p2f_values(row, p2f_m, f2p_m)

                    if p2f == -1 or f2p == -1:
                        continue

                    total_f2p += f2p
                    total_p2f += p2f
            
        return total_f2p, total_p2f
    
    def write_pp_data_to_csv(self, pp_data, pp_csv):
        with open(pp_csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=["key"] + pp_sbfl_formulas + ["metallaxis", "muse"] + ["bug"])
            writer.writeheader()

            for line_key, susp_scores in pp_data.items():
                row = {"key": line_key}
                row.update(susp_scores)
                writer.writerow(row)
    
    def get_tc_cnt(self, bug_id):
        self.testcases_dir = self.dataset_dir / "test_case_info_per_bug_version" / bug_id
        failing_tcs_txt = self.testcases_dir / "failing_tcs.txt"
        passing_tcs_txt = self.testcases_dir / "passing_tcs.txt"

        fail_cnt = 0
        with open(failing_tcs_txt, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    fail_cnt += 1
        
        pass_cnt = 0
        with open(passing_tcs_txt, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    pass_cnt += 1
        
        return fail_cnt, pass_cnt
    
    # ++++++++++++++++++++++++++++++++++++
    # PART REAL WORLD BUGS FROM MUTATED BUGS
    # ++++++++++++++++++++++++++++++++++++
    def part_real_world_bugs(self, real_world_bugs):
        print(f"Parting real-world bugs from mutated bugs for {self.subject_name}:{self.dataset_name}...")
        
        # 1. make copy of dataset_dir as <dataset_dir>-mutated_bugs
        mutated_bugs_dir = self.subject_dir / f"{self.dataset_dir.name}-mutated_bugs"
        if mutated_bugs_dir.exists():
            shutil.rmtree(mutated_bugs_dir)
        shutil.copytree(self.dataset_dir, mutated_bugs_dir)

        # 2. make copy of dataset_dir as <dataset_dir>-real_world_bugs
        real_world_bugs_dir = self.subject_dir / f"{self.dataset_dir.name}-real_world_bugs"
        if real_world_bugs_dir.exists():
            shutil.rmtree(real_world_bugs_dir)
        shutil.copytree(self.dataset_dir, real_world_bugs_dir)

        # 3. remove real-world bugs from <dataset_dir>-mutated_bugs
        self.remove_bugs(mutated_bugs_dir, real_world_bugs, keep_real_bugs=False)
        self.remove_bugs(real_world_bugs_dir, real_world_bugs, keep_real_bugs=True)
    
    def remove_bugs(self, mutated_bugs_dir, real_world_bugs, keep_real_bugs=False):
        file_data = self.return_dirs_and_files(mutated_bugs_dir)

        # 1. remove bug dirs
        self.remove_dirs(file_data["buggy_code_file_dir"], real_world_bugs, keep_real_bugs)
        self.remove_dirs(file_data["test_case_info_dir"], real_world_bugs, keep_real_bugs)
        
        # 2. remove bug files
        self.remove_files(file_data["buggy_line_key_dir"], real_world_bugs, keep_real_bugs)
        self.remove_files(file_data["FL_features_dir"], real_world_bugs, keep_real_bugs)
        self.remove_files(file_data["FL_feature_with_susp_score_dir"], real_world_bugs, keep_real_bugs)
        self.remove_files(file_data["postprocessed_coverage_dir"], real_world_bugs, keep_real_bugs)
    
    def remove_dirs(self, dir_path, real_world_bugs, keep_real_bugs):
        for bug_dir in dir_path.iterdir():
            if bug_dir.name in real_world_bugs and not keep_real_bugs:
                shutil.rmtree(bug_dir)
            elif bug_dir.name not in real_world_bugs and keep_real_bugs:
                shutil.rmtree(bug_dir)
    
    def remove_files(self, file_path, real_world_bugs, keep_real_bugs):
        for file in file_path.iterdir():
            bug_name = file.name.split(".")[0]
            if bug_name in real_world_bugs and not keep_real_bugs:
                file.unlink()
            elif bug_name not in real_world_bugs and keep_real_bugs:
                file.unlink()

    
    def return_dirs_and_files(self, dataset_dir):
        buggy_code_file_dir = dataset_dir / "buggy_code_file_per_bug_version"
        buggy_line_key_dir = dataset_dir / "buggy_line_key_per_bug_version"
        FL_features_dir = dataset_dir / "FL_features_per_bug_version"
        FL_feature_with_susp_score_dir = dataset_dir / "FL_features_per_bug_version_with_susp_scores"
        postprocessed_coverage_dir = dataset_dir / "postprocessed_coverage_per_bug_version"
        test_case_info_dir = dataset_dir / "test_case_info_per_bug_version"
        assert buggy_code_file_dir.exists(), f"Error: {buggy_code_file_dir} does not exist"
        assert buggy_line_key_dir.exists(), f"Error: {buggy_line_key_dir} does not exist"
        assert FL_features_dir.exists(), f"Error: {FL_features_dir} does not exist"
        assert FL_feature_with_susp_score_dir.exists(), f"Error: {FL_feature_with_susp_score_dir} does not exist"
        assert postprocessed_coverage_dir.exists(), f"Error: {postprocessed_coverage_dir} does not exist"
        assert test_case_info_dir.exists(), f"Error: {test_case_info_dir} does not exist"
        
        bug_version_mutation_info_csv = dataset_dir / "bug_version_mutation_info.csv"
        document_md = dataset_dir / f"document-{self.subject_name}.md"
        susp_score_py = dataset_dir / "susp_score.py"
        assert bug_version_mutation_info_csv.exists(), f"Error: {bug_version_mutation_info_csv} does not exist"
        assert document_md.exists(), f"Error: {document_md} does not exist"
        assert susp_score_py.exists(), f"Error: {susp_score_py} does not exist"

        data = {
            "buggy_code_file_dir": buggy_code_file_dir,
            "buggy_line_key_dir": buggy_line_key_dir,
            "FL_features_dir": FL_features_dir,
            "FL_feature_with_susp_score_dir": FL_feature_with_susp_score_dir,
            "postprocessed_coverage_dir": postprocessed_coverage_dir,
            "test_case_info_dir": test_case_info_dir,
            "bug_version_mutation_info_csv": bug_version_mutation_info_csv,
            "document_md": document_md,
            "susp_score_py": susp_score_py
        }
        return data





