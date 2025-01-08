from tqdm import tqdm

# from lib.utils import *
# from lib.susp_score_formula import *
# from analysis.rank_utils import *
from analysis.analysis_utils import *

from lib.experiment import Experiment
from lib.database import CRUD


class Postprocessor:
    def __init__(
        self, subject_name, experiment_name,
    ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name

        self.experiment = Experiment()
        self.experiment.init_analysis_config()
        # Settings for database
        self.host = self.experiment.experiment_config["database"]["host"]
        self.port = self.experiment.experiment_config["database"]["port"]
        self.user = self.experiment.experiment_config["database"]["user"]
        self.password = self.experiment.experiment_config["database"]["password"]
        self.database = self.experiment.experiment_config["database"]["database"]

        self.db = CRUD(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def run(self):
        # 0. Add missing features in line_info table
        self.add_missing_features()

        # 1. Calculate and write both sbfl and mbfl features
        self.calc_and_write_dynamic_features()
 
    

    def add_missing_features(self):
        # add sbfl features on line_info table
        for sbfl_features in pp_sbfl_formulas:
            feature_name = sbfl_features.lower()
            feature_name = feature_name.replace("+", "_")
            if not self.db.column_exists("line_info", feature_name):
                self.db.add_column("line_info", f"{feature_name} FLOAT DEFAULT NULL")
        
        # add muse_score, met_score on line_info table
        if not self.db.column_exists("line_info", "muse_score"):
            self.db.add_column("line_info", "muse_score FLOAT DEFAULT 0.0")
        if not self.db.column_exists("line_info", "met_score"):
            self.db.add_column("line_info", "met_score FLOAT DEFAULT 0.0")
    
    def calc_and_write_dynamic_features(self):
        # get target buggy version list
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)

        self.buggy_lines_selected_cnt = 0
        for buggy_version in tqdm(target_buggy_version_list, desc="Calculating dynamic features"):
            self.calc_and_write_mbfl_features(buggy_version)
            self.calc_and_write_sbfl_features(buggy_version)
        
        buggy_line_included_probability = (self.buggy_lines_selected_cnt / len(target_buggy_version_list)) * 100
        print(f"Probability of buggy line inclusion: {buggy_line_included_probability:.2f}%")
    

    # ========================================
    # ========= SBFL related functions =======
    # ========================================
    def calc_and_write_sbfl_features(self, buggy_version):
        bug_idx = buggy_version[0]
        version = buggy_version[1]
        buggy_file = buggy_version[2]
        buggy_function = buggy_version[3]
        buggy_lineno = buggy_version[4]
        buggy_line_idx = buggy_version[5]
        num_failing_tcs = buggy_version[6]
        num_passing_tcs = buggy_version[7]
        num_ccts = buggy_version[8]
    
        line2spectrum = get_spectrum(bug_idx, self.db)

        # Get SBFL scores for targetted lines
        line2sbfl = measure_sbfl_scores(line2spectrum, num_failing_tcs, num_passing_tcs, num_ccts, self.experiment.analysis_config["include_cct"])

        # Update line_info table with SBFL scores
        update_line_info_table_with_sbfl_scores(bug_idx, line2sbfl, self.db)
    


    # ========================================
    # ========= MBFL related functions =======
    # ========================================
    def calc_and_write_mbfl_features(self, buggy_version):
        bug_idx = buggy_version[0]
        version = buggy_version[1]
        buggy_file = buggy_version[2]
        buggy_function = buggy_version[3]
        buggy_lineno = buggy_version[4]
        buggy_line_idx = buggy_version[5]
        num_failing_tcs = buggy_version[6]
        num_passing_tcs = buggy_version[7]
        num_ccts = buggy_version[8]
        num_total_lines = buggy_version[9]


        # Get lines that we target to analyze for MBFL
        if self.experiment.analysis_config["mbfl_method"] == "for_random_mbfl":
            max_lines_for_random = self.experiment.analysis_config["max_lines_for_random"]
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    self.experiment.analysis_config["mbfl_method"]: True
                },
                special=f"ORDER BY RANDOM() LIMIT {max_lines_for_random}"
            )
        else:
            num_lines_for_random = int(num_total_lines * self.experiment.analysis_config["sbfl_ranked_rate"])
            sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    self.experiment.analysis_config["mbfl_method"]: True
                },
                special=f"ORDER BY {sbfl_standard} LIMIT {num_lines_for_random}"
            )
        
        if self.experiment.analysis_config["deliberate_inclusion"]:
            # Make sure to add buggy line to target_line_idx
            if buggy_line_idx not in target_line_idx:
                target_line_idx.append((buggy_line_idx, buggy_file, buggy_function, buggy_lineno))
        
        # map line_idx to line_info map
        line_idx2line_info = {}
        for row in target_line_idx:
            line_idx = row[0]
            line_info = {
                "file": row[1],
                "function": row[2],
                "lineno": row[3]
            }
            line_idx2line_info[line_idx] = line_info

        # Check if buggy line is selected
        if buggy_line_idx in line_idx2line_info:
            self.buggy_lines_selected_cnt += 1

        # Get all mutants generated on target lines
        lines_idx2mutant_idx = get_mutations_on_target_lines(bug_idx, line_idx2line_info, self.db)
        
        # Measure MBFL score for targetted lines
        version_data = measure_mbfl_scores(
            line_idx2line_info,
            lines_idx2mutant_idx,
            num_failing_tcs,
            self.experiment.analysis_config["mut_cnt_config"][-1],
            self.experiment.analysis_config
        )
        version_data["total_num_of_failing_tcs"] = num_failing_tcs

        # Update line_info table with met_score, muse_score
        update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx, self.db)
