import csv
import json

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
        self.pp_fl_features_dir.mkdir(exist_ok=True, parents=True)

    def run(self):
        print(">> Postprocessing FL features")
        for feature_csv in self.feature_csv_list:
            print(f"Processing {feature_csv.name}...")

            pp_data = self.process_feature_csv(feature_csv)
            pp_csv = self.pp_fl_features_dir / feature_csv.name
            self.write_pp_data_to_csv(pp_data, pp_csv)
            break
    
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
