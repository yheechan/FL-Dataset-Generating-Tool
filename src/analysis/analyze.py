from copy import deepcopy
import random
import subprocess as sp
import csv
import json
import math
import pandas as pd
import matplotlib.pyplot as plt
import shutil
from sklearn.metrics.pairwise import cosine_similarity
import multiprocessing
import torch

from lib.utils import *
from analysis.individual import Individual
from lib.experiment import Experiment
from analysis.rank_utils import *
from analysis.analysis_utils import *

from lib.experiment import Experiment
from lib.database import CRUD
from lib.config import set_seed
from tqdm import tqdm


class Analyze:
    def __init__(
            self, subject_name, experiment_name, verbose=False,
        ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name
        self.verbose = verbose

        self.subject_out_dir = out_dir / self.subject_name

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


    def run(self, analysis_criteria, type_name=None, batch_size=None):
        for ana_type in analysis_criteria:
            if ana_type == 1:
                self.analyze01()
            elif ana_type == 2:
                if type_name is None:
                    print("Please provide type_name for analysis criteria 2")
                    return
                self.analyze02(type_name)
            elif ana_type == 3:
                self.analyze03()
            elif ana_type == 4:
                self.analyze04()
            elif ana_type == 5:
                self.analyze05()
            elif ana_type == 6:
                self.analyze06()
            elif ana_type == 7:
                self.analyze07()
            elif ana_type == 8:
                self.analyze08()
            elif ana_type == 9:
                if batch_size is None:
                    print("Please provide batch_size for analysis criteria 9")
                    return
                self.analyze09(batch_size)
            elif ana_type == 10:
                self.analyze10()
            elif ana_type == 11:
                self.analyze11()



    def analyze01(self):
        """
        [stage03] analyze01: Analyze test cases and coverage statistics
            for all buggy versions resulting from prerequisite data preparation
        """
        columns = [
            "version", "buggy_file", "buggy_function", "buggy_lineno",
            "num_failing_tcs", "num_passing_tcs", "num_ccts", "num_total_tcs",
            "num_lines_executed_by_failing_tcs", "num_lines_executed_by_passing_tcs",
            "num_lines_executed_by_ccts", "num_total_lines_executed",
            "num_total_lines",
            "num_funcs_executed_by_failing_tcs", "num_total_funcs",
        ]
        col_str = ", ".join(columns)

        # 1. Retrieve list of buggy versions
        res = self.db.read(
            "bug_info",
            columns=col_str,
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name,
                "mbfl": True
            }
        )

        # 2. Calculate line coverage for each version
        columns.extend(["fail_line_cov", "pass_line_cov", "cct_line_cov", "total_line_cov"])
        analysis_result = {}
        total_result = {}
        for row in res:
            # 3. Record analysis result
            for key_num, key_val in enumerate(row):
                if key_num == 0:
                    version = key_val
                    analysis_result[version] = {}
                else:
                    analysis_result[version][columns[key_num]] = key_val

            fail_line_cov = (analysis_result[version]["num_lines_executed_by_failing_tcs"] \
                                / analysis_result[version]["num_total_lines"]) * 100
            pass_line_cov = (analysis_result[version]["num_lines_executed_by_passing_tcs"] \
                                / analysis_result[version]["num_total_lines"]) * 100
            cct_line_cov = (analysis_result[version]["num_lines_executed_by_ccts"] \
                                / analysis_result[version]["num_total_lines"]) * 100
            total_line_cov = (analysis_result[version]["num_total_lines_executed"] \
                                / analysis_result[version]["num_total_lines"]) * 100

            analysis_result[version]["fail_line_cov"] = fail_line_cov
            analysis_result[version]["pass_line_cov"] = pass_line_cov
            analysis_result[version]["cct_line_cov"] = cct_line_cov
            analysis_result[version]["total_line_cov"] = total_line_cov
            
            for key in list(analysis_result[version].keys())[3:]:
                if key not in total_result:
                    total_result[key] = []
                total_result[key].append(analysis_result[version][key])

        # print(json.dumps(analysis_result, indent=2))
        print(f"Average results for {len(analysis_result)} versions:")
        for key in total_result:
            print(f"\t{key}: {sum(total_result[key]) / len(total_result[key])}")

        
        col_for_table = [
            "subject TEXT",
            "experiment_name TEXT",
            "bug_cnt INT",
        ]
        for col in total_result:
            col_for_table.append(f"{col} FLOAT")
        col_for_table_str = ", ".join(col_for_table)
        if not self.db.table_exists("average_statistics_info"):
            self.db.create_table(
                "average_statistics_info",
                columns=col_for_table_str
            )

        values = {}
        for key in total_result:
            values[key] = sum(total_result[key]) / len(total_result[key])
        
        values["bug_cnt"] = len(analysis_result)
        
        if not self.db.value_exists(
            "average_statistics_info",
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name
            }):

            cols = ", ".join(["subject", "experiment_name"])
            vals = f"'{self.subject_name}', '{self.experiment_name}'"
            
            self.db.insert("average_statistics_info", columns=cols, values=vals)
        
        self.db.update(
            "average_statistics_info",
            set_values=values,
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name
            }
        )

        print(f"[stage03-analyze01] Average statistics for {self.subject_name} has been saved to database")


    def analyze02(self, type_name):
        """
        {
            "list_of_line_selection_methods": [
                "all_fails",
                "rand",
                "sbfl"
            ],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.2,
            "mut_cnt_config": [
                3
            ],
            "list_of_mutant_num_methods": [
                "all_fails",
                "reduced_num_mut",
                "sbfl"
            ],
            "mutant_num_method": "reduced_num_mut",
            "mutant_num_std": [
                3,
                3,
                3
            ],
            "list_of_tc_reduction_methods": [
                "all",
                "random_rate",
                "random_equal",
                "branch_cov_rate",
                "branch_cov_equal",
                "line_selective_reduction"
            ],
            "tc_reduction_method": "random_rate",
            "tc_reduction_rate": 0.1,
            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": false,
            "apply_heuristic": false,
            "versions_to_remove": [],
            "deliberate_inclusion": false
        }
        """
        """
        [stage05] analyze02: Analyze MBFL results
            for all buggy versions resulting from MBFL feature extraction
            and save the final results to file system for ML learning
        """
        self.subject_out_dir = out_dir / self.subject_name
        self.analysis_dir = self.subject_out_dir / "analysis"

        self.type_dir = self.analysis_dir / type_name
        if self.type_dir.exists():
            print(f"Analysis directory for {type_name} already exists. Exiting...")
            exit()
        
        self.features_dir = self.type_dir / "fl_features"
        if self.features_dir.exists():
            shutil.rmtree(self.features_dir)
        self.features_dir.mkdir(parents=True, exist_ok=True)

        self.utilized_mutation_info_dir = self.type_dir / "utilized_mutation_info"
        if self.utilized_mutation_info_dir.exists():
            shutil.rmtree(self.utilized_mutation_info_dir)
        self.utilized_mutation_info_dir.mkdir(parents=True, exist_ok=True)

        self.utilized_tc_info_dir = self.type_dir / "utilized_tc_info"
        if self.utilized_tc_info_dir.exists():
            shutil.rmtree(self.utilized_tc_info_dir)
        self.utilized_tc_info_dir.mkdir(parents=True, exist_ok=True)


        # add muse_score, met_score on line_info table
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            for sub_form in sub_form_list:
                if not self.db.column_exists("line_info", sub_form):
                    self.db.add_column("line_info", f"{sub_form} FLOAT DEFAULT -10.0")
        
        # add sbfl on line_info table
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            for sub_form in sub_form_list:
                if not self.db.column_exists("line_info", sub_form):
                    self.db.add_column("line_info", f"{sub_form} FLOAT DEFAULT NULL")


        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)
        
        fl_features = ["ep", "ef", "np", "nf"]
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            fl_features.extend(sub_form_list)
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            fl_features.extend(sub_form_list)

        features = ["line_idx", "file", "function", "lineno", "is_buggy_line"] + fl_features
        features_str = ", ".join(features)

        # For each buggy version with MBFL feature
        mbfl_overal_data_json = self.type_dir / "mbfl_overall_data.json"
        if not mbfl_overal_data_json.exists():
            overall_data = {}
            for buggy_version in tqdm(target_buggy_version_list, desc=f"Analyzing buggy versions for MBFL ({type_name})"):
                bug_idx = buggy_version[0]
                version = buggy_version[1]
                buggy_file = buggy_version[2]
                buggy_function = buggy_version[3]
                buggy_lineno = buggy_version[4]
                buggy_line_idx = buggy_version[5]
                total_num_failing_tcs = buggy_version[6]
                total_num_passing_tcs = buggy_version[7]
                num_ccts = buggy_version[8]
                num_total_lines = buggy_version[9]
                num_lines_executed_by_failing_tcs = buggy_version[10]
                num_total_tcs = buggy_version[11]

                self.reset_line_info_table(bug_idx, self.db)
                line_data = self.get_line_data(features, features_str, bug_idx, self.db)

                # RQ4: Reducint Passing TCs
                self.utilizing_tcs_list = self.get_utilizing_tcs_list(bug_idx, self.db)

                num_failing_tcs, num_passing_tcs, num_ccts = 0, 0, 0
                for tc in self.utilizing_tcs_list:
                    if tc[1] == "fail":
                        num_failing_tcs += 1
                    elif tc[1] == "pass":
                        num_passing_tcs += 1
                    elif tc[1] == "cct":
                        num_ccts += 1


                # For this buggy version calculate SBFL scores
                # write sbfl suspiciousness to line_info table
                set_spectrum(bug_idx, line_data, self.db, self.utilizing_tcs_list)
                set_sbfl_scores(line_data, num_failing_tcs, num_passing_tcs, num_ccts)
                update_line_info_table_with_sbfl_scores(bug_idx, line_data, self.db)

                # Get lines that we target to analyze for MBFL
                target_line_idx = self.get_target_line_idx(
                    bug_idx,
                    self.experiment.analysis_config["line_selection_rate"],
                    self.experiment.analysis_config["line_selection_method"],
                    num_lines_executed_by_failing_tcs
                )
                target_line_idx_copied = deepcopy(target_line_idx)

                sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
                # map line_idx to line_info map
                line_idx2line_info = {}
                for row in target_line_idx_copied:
                    line_idx = row[0]
                    line_idx2line_info[line_idx] = {
                        "file": row[1],
                        "function": row[2],
                        "lineno": row[3],
                        sbfl_standard: row[4]
                    }

                # Get all mutants generated on target lines
                lines_idx2mutant_idx = get_mutations_on_target_lines(
                    bug_idx, line_idx2line_info,
                    self.db, self.utilizing_tcs_list,
                    self.experiment.analysis_config["tc_reduction_method"],
                    buggy_line_idx,
                    self.experiment.analysis_config["include_cct"],
                )
                debug_print(self.verbose, f">> Found {len(lines_idx2mutant_idx)} lines with mutants")

                for mtc in self.experiment.analysis_config["mut_cnt_config"]:
                    if mtc not in overall_data:
                        overall_data[mtc] = {}
                    for iter_num in range(self.experiment.analysis_config["experiment_repeat"]):

                        # map line_idx to line_info map
                        line_idx2line_info = {}
                        for row in target_line_idx_copied:
                            line_idx = row[0]
                            line_idx2line_info[line_idx] = {
                                "file": row[1],
                                "function": row[2],
                                "lineno": row[3],
                                sbfl_standard: row[4]
                            }
                        debug_print(self.verbose, f">> Selected {len(line_idx2line_info)} lines for MBFL analysis")

                        version_data = self.analyze_bug_version_for_mbfl(
                            line_data,
                            line_idx2line_info, lines_idx2mutant_idx,
                            buggy_version, mtc, iter_num,
                            self.utilizing_tcs_list
                        )
                        
                        if version_data["version"] not in overall_data[mtc]:
                            overall_data[mtc][version_data["version"]] = []
                        overall_data[mtc][version_data["version"]].append(version_data)
        else:
            with open(mbfl_overal_data_json, "r") as f:
                overall_data = json.load(f)

        if self.experiment.analysis_config["apply_heuristic"]:
            rm_len = len(self.experiment.analysis_config["versions_to_remove"])
            print(f"Versions to remove: {rm_len}")
            for version in self.experiment.analysis_config["versions_to_remove"]:
                for mtc in overall_data:
                    if version in overall_data[mtc]:
                        overall_data[mtc].pop(version)

        average_overall_data = {}
        for mtc in overall_data:
            average_overall_data[mtc] = []
            num_failing_tcs = []
            num_utilized_mutants = []
            exec_time = []
            met_rank = []
            muse_rank = []
            met_acc5 = []
            met_acc10 = []
            muse_acc5 = []
            muse_acc10 = []
            
            for iter_cnt in range(self.experiment.analysis_config["experiment_repeat"]):
                for version, data_list in overall_data[mtc].items():
                    num_failing_tcs.append(data_list[iter_cnt]["total_num_of_failing_tcs"])
                    num_utilized_mutants.append(data_list[iter_cnt]["total_num_of_utilized_mutants"])
                    exec_time.append(data_list[iter_cnt]["total_build_time"] + data_list[iter_cnt]["total_tc_execution_time"])
                    met_rank.append(data_list[iter_cnt]["met_rank"])
                    muse_rank.append(data_list[iter_cnt]["muse_rank"])
                    met_acc5.append(1 if data_list[iter_cnt]["met_rank"] <= 5 else 0)
                    met_acc10.append(1 if data_list[iter_cnt]["met_rank"] <= 10 else 0)
                    muse_acc5.append(1 if data_list[iter_cnt]["muse_rank"] <= 5 else 0)
                    muse_acc10.append(1 if data_list[iter_cnt]["muse_rank"] <= 10 else 0)
                
                iter_data = {
                    "num_failing_tcs": sum(num_failing_tcs) / len(num_failing_tcs),
                    "num_utilized_mutants": sum(num_utilized_mutants) / len(num_utilized_mutants),
                    "exec_time": sum(exec_time) / len(exec_time),
                    "met_rank": sum(met_rank) / len(met_rank),
                    "muse_rank": sum(muse_rank) / len(muse_rank),
                    "met_acc5": sum(met_acc5) / len(met_acc5),
                    "met_acc10": sum(met_acc10) / len(met_acc10),
                    "muse_acc5": sum(muse_acc5) / len(muse_acc5),
                    "muse_acc10": sum(muse_acc10) / len(muse_acc10)
                }

                average_overall_data[mtc].append(iter_data)
        
        # Save overal_data json and csv
        with open(self.type_dir / "mbfl_overall_data.json", "w") as f:
            overall_data_native = convert_to_native(overall_data)
            json.dump(overall_data_native, f, indent=2)
        
        with open(self.type_dir / "mbfl_overall_data.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow([
                "mtc", "iter_cnt", "bug_idx", "version", "buggy_file", "buggy_function", "buggy_lineno",
                "total_num_of_failing_tcs", "total_num_of_utilized_mutants",
                "total_build_time", "total_tc_execution_time",
                "met_rank", "muse_rank", "total_number_of_functions"
            ])
            for mtc in overall_data:
                for iter_cnt in range(self.experiment.analysis_config["experiment_repeat"]):
                    for version, data_list in overall_data[mtc].items():
                        data = data_list[iter_cnt]
                        writer.writerow([
                            mtc, iter_cnt, data["bug_idx"], data["version"], data["buggy_file"], data["buggy_function"],
                            data["buggy_lineno"], data["total_num_of_failing_tcs"], data["total_num_of_utilized_mutants"],
                            data["total_build_time"], data["total_tc_execution_time"],
                            data["met_rank"], data["muse_rank"], data["total_number_of_functions"]
                        ])
        
        # Draw a line graph where x-axis is mtc, y-axis is met_acc5, met_acc10, muse_acc5, muse_acc10
        mtc_values = list(average_overall_data.keys())
        # average_overall_data[mtc] has EXPERIMENT_REPEAT amount of data
        # I need to get average, upper, and lower for each mtc on met_acc5, met_acc10, muse_acc5, muse_acc10

        met_acc5_avg = []
        met_acc5_upper = []
        met_acc5_lower = []
        met_acc10_avg = []
        met_acc10_upper = []
        met_acc10_lower = []
        muse_acc5_avg = []
        muse_acc5_upper = []
        muse_acc5_lower = []
        muse_acc10_avg = []
        muse_acc10_upper = []
        muse_acc10_lower = []
        exec_time_avg = []
        exec_time_upper = []
        exec_time_lower = []
        
        for mtc in average_overall_data:
            met_acc5_values = [data["met_acc5"] for data in average_overall_data[mtc]]
            met_acc10_values = [data["met_acc10"] for data in average_overall_data[mtc]]
            muse_acc5_values = [data["muse_acc5"] for data in average_overall_data[mtc]]
            muse_acc10_values = [data["muse_acc10"] for data in average_overall_data[mtc]]

            met_acc5_avg.append(sum(met_acc5_values) / len(met_acc5_values))
            met_acc5_upper.append(max(met_acc5_values))
            met_acc5_lower.append(min(met_acc5_values))
            met_acc10_avg.append(sum(met_acc10_values) / len(met_acc10_values))
            met_acc10_upper.append(max(met_acc10_values))
            met_acc10_lower.append(min(met_acc10_values))
            muse_acc5_avg.append(sum(muse_acc5_values) / len(muse_acc5_values))
            muse_acc5_upper.append(max(muse_acc5_values))
            muse_acc5_lower.append(min(muse_acc5_values))
            muse_acc10_avg.append(sum(muse_acc10_values) / len(muse_acc10_values))
            muse_acc10_upper.append(max(muse_acc10_values))
            muse_acc10_lower.append(min(muse_acc10_values))

            # get exec_time in hours
            exec_time_values = [data["exec_time"] / 3600 for data in average_overall_data[mtc]]
            exec_time_avg.append(sum(exec_time_values) / len(exec_time_values))
            exec_time_upper.append(max(exec_time_values))
            exec_time_lower.append(min(exec_time_values))

        plt.figure(figsize=(10, 6))
        plt.plot(mtc_values, met_acc5_avg, marker='o', label='Metallaxis acc@5')
        # plt.fill_between(mtc_values, met_acc5_lower, met_acc5_upper, alpha=0.2)
        plt.plot(mtc_values, met_acc10_avg, marker='o', label='Metallaxis acc@10')
        # plt.fill_between(mtc_values, met_acc10_lower, met_acc10_upper, alpha=0.2)
        plt.plot(mtc_values, muse_acc5_avg, marker='o', label='MUSE acc@5')
        # plt.fill_between(mtc_values, muse_acc5_lower, muse_acc5_upper, alpha=0.2)
        plt.plot(mtc_values, muse_acc10_avg, marker='o', label='MUSE acc@10')
        # plt.fill_between(mtc_values, muse_acc10_lower, muse_acc10_upper, alpha=0.2)
        plt.xlabel('Max Mutants Per Line')
        plt.ylabel('Accuracy')
        plt.title('Accuracy vs Max Mutants Per Line')
        # plt.ylim(0.0, 1.0)
        plt.legend()
        plt.grid(True)
        plt.savefig(self.type_dir / "accuracy_vs_MMPL.png")
        plt.show()

        # Draw a line graph where x-axis is mtc, y-axis is exec_time in hours, the data is in seconds

        plt.figure(figsize=(10, 6))
        plt.plot(mtc_values, exec_time_avg, marker='o', label='Execution Time (hours)')
        # plt.fill_between(mtc_values, exec_time_lower, exec_time_upper, alpha=0.2)
        plt.xlabel('Max Mutants Per Line')
        plt.ylabel('Execution Time (hours)')
        plt.title('Execution Time vs Max Mutants Per Line')
        plt.legend()
        plt.grid(True)
        plt.savefig(self.type_dir / "execution_time_vs_MMPL.png")
        plt.show()

        with open(self.type_dir / "parameters.json", "w") as f:
            json.dump(self.experiment.analysis_config, f, indent=2)
        
        # print number of buggy versions
        for mtc in overall_data:
            print(f"Number of buggy versions for mtc={mtc}: {len(overall_data[mtc])}")


    # +++++++++++++++++++++++
    # HELPER FUNCTIONS FOR ANALYZE02
    # +++++++++++++++++++++++
    def get_line_data(self, features, features_str, bug_idx, db):
        rows = db.read(
            "line_info",
            columns=features_str,
            conditions={"bug_idx": bug_idx},
            special=" ORDER BY line_idx ASC"
        )

        line_data = {}
        for line_info in rows:
            line_idx = line_info[0]
            assert line_idx not in line_data
            line_data[line_idx] = {}
            for idx, feature in enumerate(features):
                line_data[line_idx][feature] = line_info[idx]

        return line_data
    
    def get_utilizing_tcs_list(self, bug_idx, db):
        """
        Get list of utilizing test cases for a bug_idx
        """
        withCCT = self.experiment.analysis_config["include_cct"]
        tc_reduction_method = self.experiment.analysis_config["tc_reduction_method"]
        tc_reduction_rate = self.experiment.analysis_config["tc_reduction_rate"]

        failing_tcs = db.read(
            "tc_info",
            columns="tc_idx, tc_result, cov_bit_seq, similarity, tc_execution_time_duration, tc_name",
            conditions={
                "bug_idx": bug_idx,
                "tc_result": "fail"
            },
            special="ORDER BY tc_idx ASC"
        )
        
        special_str = "AND (tc_result = 'pass'"
        if withCCT or tc_reduction_method == "line_selective_reduction":
            special_str += " OR tc_result = 'cct'"
        special_str += ")"
        special_str += " ORDER BY similarity DESC"

        passing_tcs = db.read(
            "tc_info",
            columns="tc_idx, tc_result, cov_bit_seq, similarity, tc_execution_time_duration, tc_name",
            conditions={
                "bug_idx": bug_idx
            },
            special=special_str
        )

        if tc_reduction_method == "all" or tc_reduction_method == "line_selective_reduction":
            utilizing_tcs_list = failing_tcs + passing_tcs
        elif tc_reduction_method == "random_rate":
            limit = int(len(passing_tcs) * tc_reduction_rate)
            if limit == 0:
                limit = 1
            passing_tcs = random.sample(passing_tcs, limit)
            utilizing_tcs_list = failing_tcs + passing_tcs
        elif tc_reduction_method == "random_equal":
            limit = len(failing_tcs)
            if len(passing_tcs) < limit:
                limit = len(passing_tcs)
            passing_tcs = random.sample(passing_tcs, limit)
            utilizing_tcs_list = failing_tcs + passing_tcs
        elif tc_reduction_method == "branch_cov_rate":
            limit = int(len(passing_tcs) * tc_reduction_rate)
            if limit == 0:
                limit = 1
            passing_tcs = passing_tcs[:limit]
            utilizing_tcs_list = failing_tcs + passing_tcs
        elif tc_reduction_method == "branch_cov_equal":
            limit = len(failing_tcs)
            if len(passing_tcs) < limit:
                limit = len(passing_tcs)
            passing_tcs = passing_tcs[:limit]
            utilizing_tcs_list = failing_tcs + passing_tcs
        else:
            print(f"Invalid tc_reduction_method: {tc_reduction_method}")

        return utilizing_tcs_list


    def get_target_line_idx(self, bug_idx, line_selection_rate, line_selection_method, num_lines_executed_by_failing_tcs):
        """
        Get target line index for MBFL analysis
        """
        sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
        if line_selection_rate == 0.0:
            return []

        if line_selection_method == "all_fails":
            target_line_idx = self.db.read(
                "line_info",
                columns=f"line_idx, file, function, lineno, {sbfl_standard}",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                }
            )
        elif line_selection_method == "rand":
            rand_num = int(num_lines_executed_by_failing_tcs * line_selection_rate)
            if rand_num == 0:
                rand_num = 1
            target_line_idx = self.db.read(
                "line_info",
                columns=f"line_idx, file, function, lineno, {sbfl_standard}",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                },
                special=f"ORDER BY RANDOM() LIMIT {rand_num}"
            )
        elif line_selection_method == "sbfl":
            sbfl_num = int(num_lines_executed_by_failing_tcs * line_selection_rate)
            if sbfl_num == 0:
                sbfl_num = 1
            target_line_idx = self.db.read(
                "line_info",
                columns=f"line_idx, file, function, lineno, {sbfl_standard}",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                },
                special=f"ORDER BY {sbfl_standard} DESC LIMIT {sbfl_num}"
            )
        elif line_selection_method == "sbfl-test":
            target_line_idx = self.db.read(
                "line_info",
                columns=f"line_idx, file, function, lineno, {sbfl_standard}",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                }
            )

        return target_line_idx

    def analyze_bug_version_for_mbfl(self, line_data,
                                     line_idx2line_info, lines_idx2mutant_idx,
                                     buggy_version, mtc, iter_num,
                                     utilizing_tcs_list
):
        """
        Analyze a single buggy version for MBFL
        """
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
        num_lines_executed_by_failing_tcs = buggy_version[10]
        num_total_tcs = buggy_version[11]
        total_num_of_failing_tcs = num_failing_tcs

        debug_print(self.verbose, f">> Analyzing {bug_idx} {version} ({buggy_file}::{buggy_function}::{buggy_lineno})")
        debug_print(self.verbose, f">> Total number of failing test cases: {total_num_of_failing_tcs}")

        # Measure MBFL score for targetted lines
        mtc_version_data, utilizing_line_idx2mutants = measure_mbfl_scores(
            line_data,
            line_idx2line_info,
            lines_idx2mutant_idx,
            total_num_of_failing_tcs,
            mtc,
            self.experiment.analysis_config
        )
        mtc_version_data["total_num_of_failing_tcs"] = total_num_of_failing_tcs

        # Update line_info table with met_score, muse_score
        # DON'T UPDATE TO REDUCE ANALYSIS TIME
        # update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx, self.db)

        # This means the last iteration of the last mtc
        if mtc == self.experiment.analysis_config["mut_cnt_config"][-1] \
            and iter_num == self.experiment.analysis_config["experiment_repeat"] - 1:
            # save fl features to csv
            self.save_fl_features_to_csv(bug_idx, version, line_data, line_idx2line_info, utilizing_line_idx2mutants, utilizing_tcs_list)
        
        # Measure rank of buggy line
        rank_data = self.measure_buggy_line_rank(bug_idx, line_data, buggy_file, buggy_function)
        # self.reset_line_info_table(bug_idx, self.db)

        version_data = {
            "bug_idx": bug_idx,
            "version": version,
            "buggy_file": buggy_file,
            "buggy_function": buggy_function,
            "buggy_lineno": buggy_lineno,
            "buggy_line_idx": buggy_line_idx,
            "total_num_of_failing_tcs": num_failing_tcs,
            "total_num_of_passing_tcs": num_passing_tcs,
            "total_num_of_ccts": num_ccts,
            "total_num_of_lines": num_total_lines,
            "total_num_of_lines_executed_by_failing_tcs": num_lines_executed_by_failing_tcs,
            "total_num_of_tcs": num_total_tcs,
        }
        total_data = {**version_data, **mtc_version_data, **rank_data}
        return total_data

    def reset_line_info_table(self, bug_idx, db):
        """
        Reset line_info table for next iteration
        """
        values = {
            "ep": 0, "ef": 0, "np": 0, "nf": 0,
            "cct_ep": 0, "cct_np": 0,
            "met_1": -10.0, "met_2": -10.0, "met_3": -10.0,
            "muse_1": -10.0, "muse_2": -10.0, "muse_3": -10.0,
            "muse_4": -10.0, "muse_5": -10.0, "muse_6": -10.0
        }
        db.update(
            "line_info",
            set_values=values,
            conditions={
                "bug_idx": bug_idx
            }
        )

    def save_fl_features_to_csv(self, bug_idx, version, line_data, line_idx2line_info, utilizing_line_idx2mutants, utilizing_tcs_list):
        """
        Save FL features to csv file
        """
        fl_features = ["ep", "ef", "np", "nf"]
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            fl_features.extend(sub_form_list)
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            fl_features.extend(sub_form_list)

        features = ["file", "function", "lineno", "is_buggy_line"] + fl_features

        with open(self.features_dir / f"{version}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(features)
            for line_idx, line_info in line_data.items():
                row = []
                for feature in features:
                    assert feature in line_info
                    row.append(line_info[feature])
                writer.writerow(row)
        
        with open(self.utilized_mutation_info_dir / f"{version}.json", "w") as f:
            
            line_mut_info = {}

            sbfl_standard = self.experiment.analysis_config["sbfl_standard"]

            for line_idx, line_info in line_idx2line_info.items():
                assert line_idx not in line_mut_info
                line_mut_info[line_idx] = {
                    "file": line_info["file"],
                    "function": line_info["function"],
                    "lineno": line_info["lineno"],
                    "sbfl_score": line_info[sbfl_standard],
                    "mutants": []
                }
                if line_idx in utilizing_line_idx2mutants:
                    line_mut_info[line_idx]["mutants"] = utilizing_line_idx2mutants[line_idx]

            json.dump(line_mut_info, f)
        
        with open(self.utilized_tc_info_dir / f"{version}.json", "w") as f:
            tc_info = {}
            for tc in utilizing_tcs_list:
                tc_idx = tc[0]
                tc_info[tc_idx] = {
                    "tc_result": tc[1],
                    "cov_bit_seq": tc[2],
                    "similarity": tc[3],
                    "tc_execution_time_duration": tc[4],
                    "tc_name": tc[5]
                }

            json.dump(tc_info, f)


    
    def measure_buggy_line_rank(self, bug_idx, line_data, buggy_file, buggy_function):
        """
        Measure rank of buggy line
        """

        # Step 1: getch relevant information
        columns = ["file", "function", "met_3", "muse_6"]
        rows = []
        for line_idx, line_info in line_data.items():
            row = [
                line_info["file"],
                line_info["function"],
                line_info["met_3"],
                line_info["muse_6"]
            ]
            rows.append(row)


        # Step2: Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows, columns=columns)
        met_df = df.copy()
        muse_df = df.copy()
        met_grouped = met_df.groupby(["file", "function"]).agg(
            met_score=("met_3", "max"),
        ).reset_index()
        muse_grouped = muse_df.groupby(["file", "function"]).agg(
            muse_score=("muse_6", "max")
        ).reset_index()

        # Step 4: Assign ranks based on met_score descening, with tie-braking rules
        met_grouped["met_rank"] = met_grouped["met_score"].rank(method="max", ascending=False).astype(int)
        muse_grouped["muse_rank"] = muse_grouped["muse_score"].rank(method="max", ascending=False).astype(int)

        # Save to tmp.csv
        # grouped.to_csv("tmp.csv", index=False)

        # Step 5: Get rank of buggy line by buggy_file, buggy_function
        met_buggy_line_rank = met_grouped[
            (met_grouped["file"] == buggy_file) & (met_grouped["function"] == buggy_function)
        ][["met_rank"]]
        muse_buggy_line_rank = muse_grouped[
            (muse_grouped["file"] == buggy_file) & (muse_grouped["function"] == buggy_function)
        ][["muse_rank"]]


        met_rank = met_buggy_line_rank["met_rank"].values[0]
        muse_rank = muse_buggy_line_rank["muse_rank"].values[0]

        total_number_of_functions = len(met_grouped)

        rank_data = {
            "met_rank": met_rank,
            "muse_rank": muse_rank,
            "total_number_of_functions": total_number_of_functions
        }

        return rank_data
    

    def analyze03(self):
        """
        [stage05] analyze03: Analyze probability that buggy line
            is within top-k percent based on sbfl suspiciousness (need analysis_config.json)
        """

        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        # "bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)

        # For each buggy version with MBFL feature
        buggy_lines_selected_cnt = 0
        number_of_lines_selected = []
        sbfl_selected_rate = []
        for buggy_version in tqdm(target_buggy_version_list, desc="Analyzing buggy versions for MBFL"):
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
            num_lines_executed_by_failing_tcs = buggy_version[10]

            # Get lines that we target to analyze for MBFL
            target_line_idx = self.get_target_line_idx(
                bug_idx,
                self.experiment.analysis_config["line_selection_rate"],
                self.experiment.analysis_config["line_selection_method"],
                num_lines_executed_by_failing_tcs
            )

            if self.experiment.analysis_config["line_selection_method"] == "sbfl":
                line_idx2line_info = {}
                for row in target_line_idx:
                    line_idx = row[0]
                    line_idx2line_info[line_idx] = {
                        "file": row[1],
                        "function": row[2],
                        "lineno": row[3],
                        "sbfl_score": row[4]
                    }
                
                # for line_idx, file, function, lineno, sbfl_score in target_line_idx:
                #     print(f"{file}::{function}::{lineno} - {sbfl_score}")
                
                # for line_idx, line_info in line_idx2line_info.items():
                #     print(f"{line_idx} - {line_info['sbfl_score']}")

                grouped_lineidx = {
                    "high": [],
                    "medium": [],
                    "low": []
                }
                lineidx_len = len(line_idx2line_info)
                for idx, line_idx in enumerate(line_idx2line_info):
                    if idx < lineidx_len / 3:
                        grouped_lineidx["high"].append(line_idx)
                    elif idx < 2 * lineidx_len / 3:
                        grouped_lineidx["medium"].append(line_idx)
                    else:
                        grouped_lineidx["low"].append(line_idx)

            top_line_idx_list = [line_idx[0] for line_idx in target_line_idx]

            # Get top-k percent of lines based on sbfl suspiciousness
            if self.experiment.analysis_config["line_selection_method"] == "sbfl-test":
                rank_no = top_line_idx_list.index(buggy_line_idx) + 1
                rank_rate = (rank_no / len(top_line_idx_list)) * 100
                sbfl_selected_rate.append(rank_rate)


            if buggy_line_idx in top_line_idx_list:
                buggy_lines_selected_cnt += 1
            
            number_of_lines_selected.append(len(top_line_idx_list))
   
        probability_within_top = buggy_lines_selected_cnt / len(target_buggy_version_list)

        rate = self.experiment.analysis_config["line_selection_rate"] * 100
        print(f"Probability that buggy line is within top-{rate}%: {probability_within_top}")

        avg_number_of_lines_selected = sum(number_of_lines_selected) / len(number_of_lines_selected)
        print(f"Average number of lines selected: {avg_number_of_lines_selected}")

        if self.experiment.analysis_config["line_selection_method"] == "sbfl-test":
            avg_sbfl_selected_rate = sum(sbfl_selected_rate) / len(sbfl_selected_rate)
            print(f"Average SBFL selected rate: {avg_sbfl_selected_rate}")

    def analyze04(self):
        """
        [stage05] analyze04: Analyze SBFL rank of buggy lines
            for all buggy versions resulting from MBFL feature extraction
        """
        subjects = [
            "zlib_ng_exp1",
            "libxml2_exp1",
            "opencv_features2d_exp1",
            "opencv_imgproc_exp1",
            "opencv_core_exp1",
            "jsoncpp_exp1",
        ]

        experiment_name = "e1"

        experiments = [
            # RQ1-1
            # [
            #     "allfails-maxMutants-excludeCCT",
            #     "allfails-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "rand50-maxMutants-excludeCCT",
            #     "rand50-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish250-maxMutants-excludeCCT",
            #     "sbflnaish250-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ1-2
            # [
            #     "sbflnaish230-maxMutants-excludeCCT",
            #     "sbflnaish230-noReduced-excludeCCT-noHeuristics"
            # ],
            # [ --> THIS WAS USED ALSO FOR RQ2
            #     "sbflnaish210-maxMutants-excludeCCT",
            #     "sbflnaish210-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish220-maxMutants-excludeCCT",
            #     "sbflnaish220-maxMutants-excludeCCT"
            # ],
            # [
            #     "sbflnaish201-maxMutants-excludeCCT",
            #     "sbflnaish201-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish200-maxMutants-excludeCCT",
            #     "sbflnaish200-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ2
            # [
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            # ],

            # [
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            # ],
            
            # [
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-noMutants-excludeCCT",
            #     "sbflnaish210-noMutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            # ],

            # RQ3
            # [
            #     "sbflnaish210-reduced1Mutants-withCCT",
            #     "sbflnaish210-reduced1Mutants-withCCT"
            # ],

            # RQ4
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10"
            # ]

            # RQ4_20 branch
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10"
            ],

            # RQ4_20 random
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10"
            ],
        ]

        for subject in subjects:
            print(f">> Analyzing {subject}")


            # Step 1: retrieve list of bug_idx where mbfl is TRUE
            # "bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
            target_buggy_version_list = get_target_buggy_version_list(subject, experiment_name, "mbfl", self.db)

            for exp_name, exp_dirname in experiments:
                type_dir = out_dir / subject / "analysis" / exp_name
                assert type_dir.exists()

                # For each buggy version with MBFL feature
                acc_5_list = []
                acc10_list = []
                rank_dataset = {}
                for buggy_version in tqdm(target_buggy_version_list, desc="Analyzing buggy versions for MBFL"):
                    bug_idx = buggy_version[0]
                    version = buggy_version[1]
                    buggy_file = buggy_version[2]
                    buggy_function = buggy_version[3]
                    buggy_lineno = int(buggy_version[4])
                    buggy_line_idx = buggy_version[5]
                    num_failing_tcs = buggy_version[6]
                    num_passing_tcs = buggy_version[7]
                    num_ccts = buggy_version[8]
                    num_total_lines = buggy_version[9]

                    features_csv = type_dir / "fl_features" / f"{version}.csv"
                    assert features_csv.exists()

                    rank_data = self.measure_sbfl_rank(bug_idx, features_csv, buggy_file, buggy_function, buggy_lineno)
                    rank_data["bug_idx"] = bug_idx
                    rank_data["version"] = version
                    rank_data["buggy_file"] = buggy_file
                    rank_data["buggy_function"] = buggy_function
                    rank_data["buggy_lineno"] = buggy_lineno
                    rank_data["buggy_line_idx"] = buggy_line_idx
                    rank_data["num_failing_tcs"] = num_failing_tcs
                    rank_data["num_passing_tcs"] = num_passing_tcs
                    rank_data["num_ccts"] = num_ccts
                    rank_data["num_total_lines"] = num_total_lines
                    rank_dataset[version] = rank_data

                    if rank_data["sbfl_rank"] <= 5:
                        acc_5_list.append(1)
                    else:
                        acc_5_list.append(0)

                    if rank_data["sbfl_rank"] <= 10:
                        acc10_list.append(1)
                    else:
                        acc10_list.append(0)
                
                acc_5 = sum(acc_5_list) / len(acc_5_list)
                acc_10 = sum(acc10_list) / len(acc10_list)

                print(f"\t>> Accuracy@5: {acc_5}")
                print(f"\t>> Accuracy@10: {acc_10}")
                
                # average_rank = sum(rank_dataset) / len(rank_dataset)
                # print(f"\t>> Average SBFL rank naish2_5: {average_rank}")

                with open(type_dir / "sbfl_rank.json", "w") as f:
                    json.dump(rank_dataset, f, indent=2)


    def measure_sbfl_rank(self, bug_idx, features_csv, buggy_file, buggy_function, buggy_lineno):
        # sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
        sbfl_standard = "naish2_5"
        rank_name = f"{sbfl_standard}_rank"
        # Step 1: getch relevant information

        columns = ["file", "function", "lineno", sbfl_standard]

        rows = []
        with open(features_csv, "r") as f:
            # file,function,lineno,is_buggy_line,ep,ef,np,nf,binary_1,gp13_1,gp13_2,gp13_3,gp13_4,jaccard_1,jaccard_2,jaccard_3,naish1_1,naish1_2,naish2_1,naish2_2,naish2_3,naish2_4,naish2_5,ochiai_1,ochiai_2,ochiai_3,ochiai_4,russel_rao_1,russel_rao_2,russel_rao_3,wong1_1,met_1,met_2,met_3,muse_1,muse_2,muse_3,muse_4,muse_5,muse_6
            # index for columns is as follows:
            # 0: file, 1: function, 2: lineno, 3: is_buggy_line,
            # 4: ep, 5: ef, 6: np, 7: nf, 8: binary_1,
            # 9: gp13_1, 10: gp13_2, 11: gp13_3, 12: gp13_4,
            # 13: jaccard_1, 14: jaccard_2, 15: jaccard_3,
            # 16: naish1_1, 17: naish1_2, 18: naish2_1, 19: naish2_2, 20:
            # naish2_3, 21: naish2_4, 22: naish2_5,
            # 23: ochiai_1, 24: ochiai_2, 25: ochiai_3, 26: ochiai_4,
            # 27: russel_rao_1, 28: russel_rao_2, 29: russel_rao_3,
            # 30: wong1_1, 31: met_1, 32: met_2, 33: met_3,
            # 34: muse_1, 35: muse_2, 36: muse_3, 37: muse_4, 38: muse_5, 39: muse_6

            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                content = [row[0], row[1], int(row[2]), float(row[22])]
                rows.append(content)


        # Step2: Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows, columns=columns)
        
        # Step 2.1: Order by sbfl_score descening
        df = df.sort_values(by=[sbfl_standard], ascending=False)
        # measure the (row_num / total rows) * 100 for buggy file, function, lineno
        sbfl_line_top_percent = (((df.index[((df["file"] == buggy_file) & (df["function"] == buggy_function) & (df["lineno"] == buggy_lineno))]) + 1) / len(df)) * 100
        # change to float from numpy.float64
        sbfl_line_top_percent = float(sbfl_line_top_percent[0])
        

        # Step 3: Group by file, function and get max sbfl_score
        grouped = df.groupby(["file", "function"]).agg(
            sbfl_score=(sbfl_standard, "max"),
        ).reset_index()
        # Step 4: Assign ranks based on met_score descening, with tie-braking rules
        grouped[rank_name] = grouped["sbfl_score"].rank(method="max", ascending=False).astype(int)

        # Save to tmp.csv
        # grouped.to_csv("tmp.csv", index=False)

        # Step 5: Get rank of buggy line by buggy_file, buggy_function
        buggy_function_rank = grouped[
            (grouped["file"] == buggy_file) & (grouped["function"] == buggy_function)
        ][[rank_name]]


        rank = buggy_function_rank[rank_name].values[0]

        total_number_of_functions = len(grouped)

        rank_data = {
            "sbfl_line_top_percent": sbfl_line_top_percent,
            "sbfl_rank": int(rank),
            "total_number_of_functions": total_number_of_functions
        }

        return rank_data
    
    def analyze05(self):
        """
        [stage05] analyze05: Download SBFL features for all buggy versions
        """
        subject_sbfl_stats_dir = self.subject_out_dir / "sbfl_stats"
        if subject_sbfl_stats_dir.exists():
            shutil.rmtree(subject_sbfl_stats_dir)
        subject_sbfl_stats_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        # "bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)

        # For each buggy version download SBFL statistics
        for buggy_version in tqdm(target_buggy_version_list, desc="Analyzing buggy versions for MBFL"):
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

            self.download_sbfl_stats(
                subject_sbfl_stats_dir, version, bug_idx,
                buggy_file, buggy_function, buggy_lineno
            )
        

    def download_sbfl_stats(self, subject_sbfl_stats_dir, version, bug_idx,
                            buggy_file, buggy_function, buggy_lineno):
        sbfl_standard = self.experiment.analysis_config["sbfl_standard"]

        # Step 1: getch relevant information
        columns = [
            "file", "function", "lineno", "ef", "nf", "ep", "np", "cct_ep", "cct_np",
            "binary_1", "gp13_4", "jaccard_3", "naish1_2", "naish2_5", "ochiai_4", "russel_rao_3", "wong1_1",
            "selected_for_mbfl", "is_buggy_line"]
        col_str = ", ".join(columns)
        rows = self.db.read(
            "line_info",
            columns=col_str,
            conditions={"bug_idx": bug_idx}
        )

        # Step2: Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows, columns=columns)

        # save to csv
        df.to_csv(subject_sbfl_stats_dir / f"{version}.csv", index=False)


    def analyze06(self):
        """
        [stage05] Analyze06: Generate figures for mbfl score and MBFL feature extraction time for subjects and analysis types below
        """
        print("Deprecated 2025-03-06 (Thursday)")
        # subjects = [
        #     "zlib_ng_TF_top30",
        #     "libxml2_TF_top30",
        #     "opencv_features2d_TF_top30",
        #     "opencv_imgproc_TF_top30",
        #     "opencv_core_TF_top30",
        #     "jsoncpp_TF_top30",
        #     "opencv_calib3d_TF_top30"
        # ]

        # selection_rate = "50"

        # analysis_types = [
        #     # "allfails-noReduced-excludeCCT-noHeuristics",
        #     # f"rand{selection_rate}-noReduced-excludeCCT-noHeuristics",
        #     # f"sbflnaish2{selection_rate}-noReduced-excludeCCT-noHeuristics",
        #     # f"sbflnaish2{selection_rate}-reduced-excludeCCT-noHeuristics",
        #     f"sbflnaish2{selection_rate}-reduced_sbflnaish2-excludeCCT-noHeuristics",
        #     f"sbflnaish2{selection_rate}-reduced_sbflnaish2-withCCT-noHeuristics",
        # ]

        # results = {}

        # for subject in subjects:
        #     analysis_dir = out_dir / subject / "analysis"

        #     if subject not in results:
        #         results[subject] = {}
            
        #     for analysis_type in analysis_types:
        #         if analysis_type not in results[subject]:
        #             results[subject][analysis_type] = {}
                
        #         analysis_type_dir = analysis_dir / analysis_type

        #         mbfl_overall_data_json = analysis_type_dir / "mbfl_overall_data.json"
        #         mbfl_overall_data = json.loads(mbfl_overall_data_json.read_text())

        #         # MUTATION # CONFIGURATION: 10
        #         for key, data in mbfl_overall_data.items():
        #             met_acc5 = 0
        #             met_acc10 = 0
        #             muse_acc5 = 0
        #             muse_acc10 = 0

        #             list_time_duration = []

        #             # VERSION
        #             for version_name, version_data in data.items():
        #                 met_rank = version_data[0]["met_rank"]
        #                 muse_rank = version_data[0]["muse_rank"]

        #                 tot_build_time = version_data[0]["total_build_time"]
        #                 tot_tc_exec_time = version_data[0]["total_tc_execution_time"]
        #                 total_time_duration = (tot_build_time + tot_tc_exec_time) / 3600
        #                 list_time_duration.append(total_time_duration)

        #                 if met_rank <= 5:
        #                     met_acc5 += 1
        #                 if met_rank <= 10:
        #                     met_acc10 += 1
        #                 if muse_rank <= 5:
        #                     muse_acc5 += 1
        #                 if muse_rank <= 10:
        #                     muse_acc10 += 1

        #             met_acc5 /= len(data)
        #             met_acc10 /= len(data)
        #             muse_acc5 /= len(data)
        #             muse_acc10 /= len(data)
        #             avg_time_duration = sum(list_time_duration) / len(list_time_duration)

        #             results[subject][analysis_type][key] = {
        #                 "met_acc5": met_acc5,
        #                 "met_acc10": met_acc10,
        #                 "muse_acc5": muse_acc5,
        #                 "muse_acc10": muse_acc10,
        #                 "avg_time_duration": avg_time_duration
        #             }


        # analysis_type_name_dict = {}
        # for analysis_type in analysis_types:
        #     if analysis_type == "allfails-noReduced-excludeCCT-noHeuristics":
        #         analysis_type_name_dict[analysis_type] = "all-lines"
        #     elif analysis_type == f"rand{selection_rate}-noReduced-excludeCCT-noHeuristics":
        #         analysis_type_name_dict[analysis_type] = "random"
        #     elif analysis_type == f"sbflnaish2{selection_rate}-noReduced-excludeCCT-noHeuristics":
        #         # analysis_type_name_dict[analysis_type] = "sbfl-based"
        #         analysis_type_name_dict[analysis_type] = "max_mutants"
        #     elif analysis_type == f"sbflnaish2{selection_rate}-reduced-excludeCCT-noHeuristics":
        #         analysis_type_name_dict[analysis_type] = "reduced_mutants_average"
        #     elif analysis_type == f"sbflnaish2{selection_rate}-reduced_sbflnaish2-excludeCCT-noHeuristics":
        #         analysis_type_name_dict[analysis_type] = "reduced_sbfl_based_withoutCCT"
        #     elif analysis_type == f"sbflnaish2{selection_rate}-reduced_sbflnaish2-withCCT-noHeuristics":
        #         analysis_type_name_dict[analysis_type] = "reduced_sbfl_based_withCCT"


        # # first make the dictionary for the data
        # time_data = {}
        # analysis_names = []
        # for subject in subjects:
        #     subject_name = "_".join(subject.split("_")[:2])
        #     if subject_name == "opencv_calib3d":
        #         subject_name = "*opencv_calib3d"

        #     time_data[subject_name] = {}
        #     for analysis_type in analysis_types:
        #         analysis_type_name = analysis_type_name_dict[analysis_type]
                
        #         if analysis_type_name not in analysis_names:
        #             analysis_names.append(analysis_type_name)
        #         time_data[subject_name][analysis_type_name] = results[subject][analysis_type]["10"]["avg_time_duration"]

        # # plot the bar chart
        # fig, ax = plt.subplots()

        # bar_width = 0.2
        # index = range(len(subjects))
        # colors = ['dimgray', 'silver', 'lime']

        # for i, analysis_type in enumerate(analysis_names):
        #     avg_time_durations = [time_data[subject][analysis_type] for subject in time_data]
        #     ax.bar([p + bar_width * i for p in index], avg_time_durations, bar_width, label=analysis_type, color=colors[i])

        # ax.set_xlabel('Subject')
        # ax.set_ylabel('Avg. time taken (hours)')
        # ax.set_title('Avg. time taken for MBFL extraction by each line selection method')
        # ax.set_xticks([p + bar_width for p in index])
        # ax.set_xticklabels(time_data, rotation=45, ha="right")
        # ax.legend()

        # plt.tight_layout()

        # # save to file
        # plt.savefig(out_dir / "mbfl_time_duration.png")

        # # measure relative reduced time against sbfl-based, random and all-lines
        # relative_time_data = {}
        # for subject in subjects:
        #     subject_name = "_".join(subject.split("_")[:2])
        #     if subject_name == "opencv_calib3d":
        #         subject_name = "*opencv_calib3d"

        #     relative_time_data[subject_name] = {}
        #     for analysis_type in analysis_types:
        #         if analysis_type == "allfails-noReduced-excludeCCT-noHeuristics":
        #             all_lines_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #         elif analysis_type == f"rand{selection_rate}-noReduced-excludeCCT-noHeuristics":
        #             random_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #         elif analysis_type == f"sbflnaish2{selection_rate}-noReduced-excludeCCT-noHeuristics":
        #             # sbfl_based_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #             max_mutants_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #         elif analysis_type == f"sbflnaish2{selection_rate}-reduced-excludeCCT-noHeuristics":
        #             reduced_mutants_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #         elif analysis_type == f"sbflnaish2{selection_rate}-reduced_sbflnaish2-excludeCCT-noHeuristics":
        #             reduced_sbfl_based_time = results[subject][analysis_type]["10"]["avg_time_duration"]
        #         elif analysis_type == f"sbflnaish2{selection_rate}-reduced_sbflnaish2-withCCT-noHeuristics":
        #             reduced_sbfl_based_withCCT_time = results[subject][analysis_type]["10"]["avg_time_duration"]
            
        #     # relative_time_data[subject_name]["all-lines"] = 0
        #     # relative_time_data[subject_name]["random"] = (random_time - all_lines_time) / all_lines_time
        #     # relative_time_data[subject_name]["sbfl-based"] = (sbfl_based_time - all_lines_time) / all_lines_time

        #     # relative_time_data[subject_name]["max_mutants"] = 0
        #     # relative_time_data[subject_name]["reduced_mutants_average"] = (reduced_mutants_time - max_mutants_time) / max_mutants_time
        #     # relative_time_data[subject_name]["reduced_sbfl_based"] = (reduced_sbfl_based_time - max_mutants_time) / max_mutants_time

        #     relative_time_data[subject_name]["reduced_sbfl_based_withoutCCT"] = 0
        #     relative_time_data[subject_name]["reduced_sbfl_based_withCCT"] = (reduced_sbfl_based_withCCT_time - reduced_sbfl_based_time) / reduced_sbfl_based_time
        
        # # write results to csv file
        # out_file = out_dir / "mbfl_scores.csv"
        # with open(out_file, "w") as f:
        #     f.write("subject,analysis_type,num_mutants,method,met_acc5,met_acc10,muse_acc5,muse_acc10,avg. time duration,rel. time diff.\n")
        #     for subject in subjects:
        #         subject_name = "_".join(subject.split("_")[:2])
        #         if subject_name == "opencv_calib3d":
        #             subject_name = "*opencv_calib3d"
        #         for analysis_type in analysis_types:
        #             analysis_type_name = analysis_type_name_dict[analysis_type]
        #             for key, data in results[subject][analysis_type].items():
        #                 # round to 2 decimal places
        #                 avg_time = round(data['avg_time_duration'], 2)
        #                 data['met_acc5'] = round((data['met_acc5'])*100, 2)
        #                 data['met_acc10'] = round((data['met_acc10'])*100, 2)
        #                 data['muse_acc5'] = round((data['muse_acc5'])*100, 2)
        #                 data['muse_acc10'] = round((data['muse_acc10'])*100, 2)
        #                 rel_time_diff = round((relative_time_data[subject_name][analysis_type_name])*100, 2)
        #                 f.write(f"{subject},{analysis_type},{key},{analysis_type_name},{data['met_acc5']},{data['met_acc10']},{data['muse_acc5']},{data['muse_acc10']},{avg_time},{rel_time_diff}\n")


    def analyze07(self,):
        """
        [stage05] Analyze07: Write the statistical numbers of raw data (mutation, tcs)
        """
        subjects = [
            "zlib_ng_exp1",
            # "libxml2_exp1",
            # "opencv_features2d_exp1",
            # "opencv_imgproc_exp1",
            # "opencv_core_exp1",
            # "jsoncpp_exp1",
        ]

        experiment_name = "e1"

        experiments = [
            # RQ1-1
            # [
            #     "allfails-maxMutants-excludeCCT",
            #     "allfails-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "rand50-maxMutants-excludeCCT",
            #     "rand50-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish250-maxMutants-excludeCCT",
            #     "sbflnaish250-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ1-2
            # [
            #     "sbflnaish230-maxMutants-excludeCCT",
            #     "sbflnaish230-noReduced-excludeCCT-noHeuristics"
            # ],
            # [ --> THIS WAS USED ALSO FOR RQ2
            #     "sbflnaish210-maxMutants-excludeCCT",
            #     "sbflnaish210-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish220-maxMutants-excludeCCT",
            #     "sbflnaish220-maxMutants-excludeCCT"
            # ],
            # [
            #     "sbflnaish201-maxMutants-excludeCCT",
            #     "sbflnaish201-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish200-maxMutants-excludeCCT",
            #     "sbflnaish200-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ2
            # [
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            # ],

            # [
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            # ],
            
            # [
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-noMutants-excludeCCT",
            #     "sbflnaish210-noMutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            # ],

            # RQ3
            # [
            #     "sbflnaish210-reduced1Mutants-withCCT",
            #     "sbflnaish210-reduced1Mutants-withCCT"
            # ],

            # RQ4
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10"
            # ]

            # RQ4_20 branch
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10"
            # ],

            # # RQ4_20 random
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30"
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10",
            #     "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10"
            # ],
            [
                "test1",
                "test1"
            ]
        ]

        for subject in subjects:
            print(f">> Analyzing {subject}")
            # 1. First get buggy line information from db
            bug_info_list = self.db.read(
                "bug_info",
                columns="bug_idx, version, buggy_file, buggy_function, buggy_lineno, num_lines_executed_by_failing_tcs, num_funcs_executed_by_failing_tcs, num_failing_tcs, num_passing_tcs, num_ccts",
                conditions={
                    "subject": subject,
                    "experiment_name": experiment_name,
                    "mbfl": True
                }
            )

            version2buggy_line_info = {}
            for bug_info in bug_info_list:
                version = bug_info[1]
                buggy_line_info = {
                    "bug_idx": bug_info[0],
                    "buggy_file": bug_info[2],
                    "buggy_function": bug_info[3],
                    "buggy_lineno": bug_info[4],
                    "num_lines_executed_by_failing_tcs": bug_info[5],
                    "num_funcs_executed_by_failing_tcs": bug_info[6],
                    "num_failing_tcs": bug_info[7],
                    "num_passing_tcs": bug_info[8],
                    "num_ccts": bug_info[9]
                }
                version2buggy_line_info[version] = buggy_line_info

            features = [
                "version",
                "num_failing_tcs", "num_passing_tcs", "num_ccts",
                "num_utilized_failing_tcs", "num_utilized_passing_tcs", "num_utilized_ccts",
                "total_num_utilized_mutants", "avg_num_utilized_mutants_per_line",
                "buggy_line_tested", "buggy_line_mut_cnt",
                "nonbuggy_line_f2p", "nonbuggy_line_p2f",
                "nonbuggy_line_f2f", "nonbuggy_line_p2p",
                "buggy_line_f2p", "buggy_line_p2f",
                "buggy_line_f2f", "buggy_line_p2p",
                "total_mut_build_time", "total_tc_exec_time",
                "total_tc_executions",
                "num_lines_executed_by_failing_tcs", "num_funcs_executed_by_failing_tcs"
            ]
            features_str = ",".join(features)
            for exp_name, exp_dirname in experiments:
                type_dir = out_dir / subject / "analysis" / exp_name
                assert type_dir.exists()
                utilized_mutation_info_dir = type_dir / "utilized_mutation_info"
                assert utilized_mutation_info_dir.exists()
                utilized_tc_info_dir = type_dir / "utilized_tc_info"
                assert utilized_tc_info_dir.exists()

                utilized_data_info_csv_fp = open(type_dir / "utilized_data_info.csv", "w")
                utilized_data_info_csv_fp.write(f"{features_str}\n")
               
                total_statistics = {
                    "version": [],
                    "num_failing_tcs": [],
                    "num_passing_tcs": [],
                    "num_ccts": [],
                    "num_utilized_failing_tcs": [],
                    "num_utilized_passing_tcs": [],
                    "num_utilized_ccts": [],
                    "total_num_utilized_mutants": [],
                    "avg_num_utilized_mutants_per_line": [],
                    "buggy_line_tested": [],
                    "buggy_line_mut_cnt": [],
                    "nonbuggy_line_f2p": [],
                    "nonbuggy_line_p2f": [],
                    "nonbuggy_line_f2f": [],
                    "nonbuggy_line_p2p": [],
                    "buggy_line_f2p": [],
                    "buggy_line_p2f": [],
                    "buggy_line_f2f": [],
                    "buggy_line_p2p": [],
                    "total_mut_build_time": [],
                    "total_tc_exec_time": [],
                    "total_tc_executions": [],
                    "num_lines_executed_by_failing_tcs": [],
                    "num_funcs_executed_by_failing_tcs": []
                }
                assert len(version2buggy_line_info) == len(list(utilized_mutation_info_dir.iterdir()))
                assert len(version2buggy_line_info) == len(list(utilized_tc_info_dir.iterdir()))


                for buggy_version, buggy_data in version2buggy_line_info.items():
                    utilized_mut_json = json.loads((utilized_mutation_info_dir / f"{buggy_version}.json").read_text())
                    utilized_tc_json = json.loads((utilized_tc_info_dir / f"{buggy_version}.json").read_text())

                    buggy_version_mut_info = {
                        "num_utilized_failing_tcs": 0,
                        "num_utilized_passing_tcs": 0,
                        "num_utilized_ccts": 0,
                        "total_num_utilized_mutants": 0,
                        "buggy_line_tested": False,
                        "buggy_line_mut_cnt": 0,
                        "nonbuggy_line_f2p": [],
                        "nonbuggy_line_p2f": [],
                        "nonbuggy_line_f2f": [],
                        "nonbuggy_line_p2p": [],
                        "buggy_line_f2p": 0,
                        "buggy_line_p2f": 0,
                        "buggy_line_f2f": 0,
                        "buggy_line_p2p": 0,
                        "total_mut_build_time": 0,
                        "total_tc_exec_time": 0,
                        "total_tc_executions": 0,
                    }

                    # mut info
                    utilized_tcs = False
                    for line, line_data in utilized_mut_json.items():
                        for mut_dict in line_data["mutants"]:
                            if line_data["file"] == buggy_data["buggy_file"] and line_data["function"] == buggy_data["buggy_function"] and line_data["lineno"] == buggy_data["buggy_lineno"]:
                                buggy_version_mut_info["buggy_line_tested"] = True
                                buggy_version_mut_info["buggy_line_mut_cnt"] = len(line_data["mutants"])
                            
                                buggy_version_mut_info["buggy_line_f2p"] += mut_dict["f2p"]
                                buggy_version_mut_info["buggy_line_p2f"] += mut_dict["p2f"]
                                buggy_version_mut_info["buggy_line_f2f"] += mut_dict["f2f"]
                                buggy_version_mut_info["buggy_line_p2p"] += mut_dict["p2p"]
                            else:
                                buggy_version_mut_info["nonbuggy_line_f2p"].append(mut_dict["f2p"])
                                buggy_version_mut_info["nonbuggy_line_p2f"].append(mut_dict["p2f"])
                                buggy_version_mut_info["nonbuggy_line_f2f"].append(mut_dict["f2f"])
                                buggy_version_mut_info["nonbuggy_line_p2p"].append(mut_dict["p2p"])
                            
                            buggy_version_mut_info["total_tc_executions"] += (
                                mut_dict["f2p"] + mut_dict["p2f"] + mut_dict["f2f"] + mut_dict["p2p"]
                            )

                            # a more fine-grained tc reduction (reduction diffierent per line)
                            if "utilized_tcs_bit_seq" in mut_dict:
                                utilized_tcs = True
                                for tc_idx, tc_bit in enumerate(mut_dict["utilized_tcs_bit_seq"]):
                                    tc_idx = str(tc_idx)
                                    tc_bit = str(tc_bit)
                                    if tc_bit == "1":
                                        assert tc_idx in utilized_tc_json
                                        buggy_version_mut_info["total_tc_exec_time"] += utilized_tc_json[tc_idx]["tc_execution_time_duration"]

                            buggy_version_mut_info["total_mut_build_time"] += mut_dict["build_time_duration"]
                        buggy_version_mut_info["total_num_utilized_mutants"] += len(line_data["mutants"])

                    if len(utilized_mut_json) == 0:
                        avg_num_utilized_mutants_per_line = 0
                    else:
                        avg_num_utilized_mutants_per_line = buggy_version_mut_info["total_num_utilized_mutants"] / len(utilized_mut_json)
                    

                    # tc_info
                    total_tc_exec_time = 0
                    for tc_idx, tc_info in utilized_tc_json.items():
                        if tc_info["tc_result"] == "fail":
                            buggy_version_mut_info["num_utilized_failing_tcs"] += 1
                        elif tc_info["tc_result"] == "pass":
                            buggy_version_mut_info["num_utilized_passing_tcs"] += 1
                        elif tc_info["tc_result"] == "cct":
                            buggy_version_mut_info["num_utilized_ccts"] += 1
                        total_tc_exec_time += tc_info["tc_execution_time_duration"]

                    if utilized_tcs == False:
                        buggy_version_mut_info["total_tc_exec_time"] = total_tc_exec_time*buggy_version_mut_info["total_num_utilized_mutants"]

                    total_statistics["version"].append(buggy_version)
                    total_statistics["num_failing_tcs"].append(buggy_data["num_failing_tcs"])
                    total_statistics["num_passing_tcs"].append(buggy_data["num_passing_tcs"])
                    total_statistics["num_ccts"].append(buggy_data["num_ccts"])
                    total_statistics["num_utilized_failing_tcs"].append(buggy_version_mut_info["num_utilized_failing_tcs"])
                    total_statistics["num_utilized_passing_tcs"].append(buggy_version_mut_info["num_utilized_passing_tcs"])
                    total_statistics["num_utilized_ccts"].append(buggy_version_mut_info["num_utilized_ccts"])
                    total_statistics["total_num_utilized_mutants"].append(buggy_version_mut_info["total_num_utilized_mutants"])
                    total_statistics["avg_num_utilized_mutants_per_line"].append(avg_num_utilized_mutants_per_line)
                    total_statistics["buggy_line_mut_cnt"].append(buggy_version_mut_info["buggy_line_mut_cnt"])
                    total_statistics["buggy_line_f2p"].append(buggy_version_mut_info["buggy_line_f2p"])
                    total_statistics["buggy_line_p2f"].append(buggy_version_mut_info["buggy_line_p2f"])
                    total_statistics["buggy_line_f2f"].append(buggy_version_mut_info["buggy_line_f2f"])
                    total_statistics["buggy_line_p2p"].append(buggy_version_mut_info["buggy_line_p2p"])
                    total_statistics["total_mut_build_time"].append(buggy_version_mut_info["total_mut_build_time"])
                    total_statistics["total_tc_exec_time"].append(buggy_version_mut_info["total_tc_exec_time"])
                    total_statistics["total_tc_executions"].append(buggy_version_mut_info["total_tc_executions"])
                    total_statistics["num_lines_executed_by_failing_tcs"].append(buggy_data["num_lines_executed_by_failing_tcs"])
                    total_statistics["num_funcs_executed_by_failing_tcs"].append(buggy_data["num_funcs_executed_by_failing_tcs"])

                    avg_nonbuggy_line_f2p = 0
                    avg_nonbuggy_line_p2f = 0
                    avg_nonbuggy_line_f2f = 0
                    avg_nonbuggy_line_p2p = 0
                    if len(buggy_version_mut_info["nonbuggy_line_f2p"]) > 0:
                        avg_nonbuggy_line_f2p = sum(buggy_version_mut_info["nonbuggy_line_f2p"]) / len(buggy_version_mut_info["nonbuggy_line_f2p"])
                    if len(buggy_version_mut_info["nonbuggy_line_p2f"]) > 0:
                        avg_nonbuggy_line_p2f = sum(buggy_version_mut_info["nonbuggy_line_p2f"]) / len(buggy_version_mut_info["nonbuggy_line_p2f"])
                    if len(buggy_version_mut_info["nonbuggy_line_f2f"]) > 0:
                        avg_nonbuggy_line_f2f = sum(buggy_version_mut_info["nonbuggy_line_f2f"]) / len(buggy_version_mut_info["nonbuggy_line_f2f"])
                    if len(buggy_version_mut_info["nonbuggy_line_p2p"]) > 0:
                        avg_nonbuggy_line_p2p = sum(buggy_version_mut_info["nonbuggy_line_p2p"]) / len(buggy_version_mut_info["nonbuggy_line_p2p"])

                    total_statistics["nonbuggy_line_f2p"].append(avg_nonbuggy_line_f2p)
                    total_statistics["nonbuggy_line_p2f"].append(avg_nonbuggy_line_p2f)
                    total_statistics["nonbuggy_line_f2f"].append(avg_nonbuggy_line_f2f)
                    total_statistics["nonbuggy_line_p2p"].append(avg_nonbuggy_line_p2p)

                    content = [
                        buggy_version,
                        buggy_data["num_failing_tcs"],
                        buggy_data["num_passing_tcs"],
                        buggy_data["num_ccts"],
                        buggy_version_mut_info["num_utilized_failing_tcs"],
                        buggy_version_mut_info["num_utilized_passing_tcs"],
                        buggy_version_mut_info["num_utilized_ccts"],
                        buggy_version_mut_info["total_num_utilized_mutants"],
                        avg_num_utilized_mutants_per_line,
                        buggy_version_mut_info["buggy_line_tested"],
                        buggy_version_mut_info["buggy_line_mut_cnt"],
                        avg_nonbuggy_line_f2p,
                        avg_nonbuggy_line_p2f,
                        avg_nonbuggy_line_f2f,
                        avg_nonbuggy_line_p2p,
                        buggy_version_mut_info["buggy_line_f2p"],
                        buggy_version_mut_info["buggy_line_p2f"],
                        buggy_version_mut_info["buggy_line_f2f"],
                        buggy_version_mut_info["buggy_line_p2p"],
                        buggy_version_mut_info["total_mut_build_time"],
                        buggy_version_mut_info["total_tc_exec_time"],
                        buggy_version_mut_info["total_tc_executions"],
                        buggy_data["num_lines_executed_by_failing_tcs"],
                        buggy_data["num_funcs_executed_by_failing_tcs"]
                    ]
                    row_content = ",".join([str(c) for c in content])
                    utilized_data_info_csv_fp.write(f"{row_content}\n")

                utilized_data_info_csv_fp.close()

                with open(type_dir / "utilized_data_avg_stats.json", "w") as f:
                    data = {
                        "total_num_versions": len(version2buggy_line_info),
                        "avg_num_failing_tcs": sum(total_statistics["num_failing_tcs"]) / len(version2buggy_line_info),
                        "avg_num_passing_tcs": sum(total_statistics["num_passing_tcs"]) / len(version2buggy_line_info),
                        "avg_num_ccts": sum(total_statistics["num_ccts"]) / len(version2buggy_line_info),
                        "avg_num_utilized_failing_tcs": sum(total_statistics["num_utilized_failing_tcs"]) / len(version2buggy_line_info),
                        "avg_num_utilized_passing_tcs": sum(total_statistics["num_utilized_passing_tcs"]) / len(version2buggy_line_info),
                        "avg_num_utilized_ccts": sum(total_statistics["num_utilized_ccts"]) / len(version2buggy_line_info),
                        "avg_num_utilized_mutants": sum(total_statistics["total_num_utilized_mutants"]) / len(version2buggy_line_info),
                        "avg_num_utilized_mutants_per_line": sum(total_statistics["avg_num_utilized_mutants_per_line"]) / len(version2buggy_line_info),
                        "avg_buggy_line_mut_cnt": sum(total_statistics["buggy_line_mut_cnt"]) / len(version2buggy_line_info),
                        "avg_nonbuggy_line_f2p": sum(total_statistics["nonbuggy_line_f2p"]) / len(version2buggy_line_info),
                        "avg_nonbuggy_line_p2f": sum(total_statistics["nonbuggy_line_p2f"]) / len(version2buggy_line_info),
                        "avg_nonbuggy_line_f2f": sum(total_statistics["nonbuggy_line_f2f"]) / len(version2buggy_line_info),
                        "avg_nonbuggy_line_p2p": sum(total_statistics["nonbuggy_line_p2p"]) / len(version2buggy_line_info),
                        "avg_buggy_line_f2p": sum(total_statistics["buggy_line_f2p"]) / len(version2buggy_line_info),
                        "avg_buggy_line_p2f": sum(total_statistics["buggy_line_p2f"]) / len(version2buggy_line_info),
                        "avg_buggy_line_f2f": sum(total_statistics["buggy_line_f2f"]) / len(version2buggy_line_info),
                        "avg_buggy_line_p2p": sum(total_statistics["buggy_line_p2p"]) / len(version2buggy_line_info),
                        "avg_total_mut_build_time": sum(total_statistics["total_mut_build_time"]) / len(version2buggy_line_info),
                        "avg_total_tc_exec_time": sum(total_statistics["total_tc_exec_time"]) / len(version2buggy_line_info),
                        "avg_total_tc_executions": sum(total_statistics["total_tc_executions"]) / len(version2buggy_line_info),
                        "avg_num_lines_executed_by_failing_tcs": sum(total_statistics["num_lines_executed_by_failing_tcs"]) / len(version2buggy_line_info),
                        "avg_num_funcs_executed_by_failing_tcs": sum(total_statistics["num_funcs_executed_by_failing_tcs"]) / len(version2buggy_line_info)
                    }
                    json.dump(data, f, indent=4)


    def analyze08(self):
        """
        [stage05] Analyze08: Conduct significance wilcoxon test on two types of a ML result data for a subeject
        """

        shape = "shape1"
        
        self.subject_out_dir = out_dir / self.subject_name
        self.analysis_dir = self.subject_out_dir / "analysis"
        self.ml_dir = self.analysis_dir / "ml"

        test_data_name = "opencv_calib3d-D0"
        # type_1 = f"HPexp/all-lines-{shape}"
        # type_2 = f"HPexp/random-{shape}"
        # type_3 = f"HPexp/sbfl-based-{shape}"

        type_1 = f"MCexp/max_mutants-{shape}"
        type_2 = f"MCexp/reduced_mutants_average-{shape}"
        type_3 = f"MCexp/reduced_sbfl_based-{shape}"

        type_1_version2rank, type_1_rank_list = self.get_version_ranks(
            self.ml_dir / type_1 / "inference" / test_data_name/ "inference-accuracy.csv")
        type_2_version2rank, type_2_rank_list = self.get_version_ranks(
            self.ml_dir / type_2 / "inference" / test_data_name / "inference-accuracy.csv")
        type_3_version2rank, type_3_rank_list = self.get_version_ranks(
            self.ml_dir / type_3 / "inference" / test_data_name / "inference-accuracy.csv")

        # assert that all keys from each type are the same
        assert type_1_version2rank.keys() == type_2_version2rank.keys()
        assert type_1_version2rank.keys() == type_3_version2rank.keys()

        key_list = list(type_1_version2rank.keys())

        # measure wilcoxon test
        import scipy.stats as stats
        statistics, pvalue = stats.wilcoxon(
            type_1_rank_list, type_3_rank_list
        )
        print("type1: ", statistics, pvalue)

        statistics, pvalue = stats.wilcoxon(
            type_2_rank_list, type_3_rank_list
        )
        print("type2: ", statistics, pvalue)


    
    def get_version_ranks(self, csv_file):
        """
        Get version ranks from csv file
        """
        ranks = {}
        rank_list = []
        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                version = row[0].split("-")[1]
                rank = int(row[1])
                ranks[version] = rank
                rank_list.append(rank)
        return ranks, rank_list


    def analyze09(self, batch_size):
        """
        [stage05] Analyze09: Conduct experiments with various hyper-parameters of model
        """

        experiments = [
            # RQ1-1
            # [
            #     "allfails-maxMutants-excludeCCT",
            #     "allfails-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "rand50-maxMutants-excludeCCT",
            #     "rand50-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish250-maxMutants-excludeCCT",
            #     "sbflnaish250-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ1-2
            # [
            #     "sbflnaish230-maxMutants-excludeCCT",
            #     "sbflnaish230-noReduced-excludeCCT-noHeuristics"
            # ],
            # [ --> THIS WAS USED ALSO FOR RQ2
            #     "sbflnaish210-maxMutants-excludeCCT",
            #     "sbflnaish210-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish220-maxMutants-excludeCCT",
            #     "sbflnaish220-maxMutants-excludeCCT"
            # ],
            # [
            #     "sbflnaish201-maxMutants-excludeCCT",
            #     "sbflnaish201-noReduced-excludeCCT-noHeuristics"
            # ],
            # [
            #     "sbflnaish200-maxMutants-excludeCCT",
            #     "sbflnaish200-noReduced-excludeCCT-noHeuristics"
            # ],

            # RQ2
            # [
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            #     "sbflnaish230-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            #     "sbflnaish230-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            #     "sbflnaish230-reduced1Mutants-excludeCCT",
            # ],

            # [
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            #     "sbflnaish220-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            #     "sbflnaish220-reduced3Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            #     "sbflnaish220-reduced1Mutants-excludeCCT",
            # ],
            
            # [
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            #     "sbflnaish210-reduced5Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            #     "sbflnaish210-reduced1Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-noMutants-excludeCCT",
            #     "sbflnaish210-noMutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            #     "sbflnaish210-reduced7Mutants-excludeCCT",
            # ],
            # [
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            #     "sbflnaish210-reduced3Mutants-excludeCCT",
            # ],

            # RQ3
            # [
            #     "sbflnaish210-reduced1Mutants-withCCT",
            #     "sbflnaish210-reduced1Mutants-withCCT"
            # ],

            # RQ4
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30"
            # ],
            # [
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10",
            #     "sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10"
            # ]

            # RQ4_20 branch
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10"
            ],

            # RQ4_20 random
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30"
            ],
            [
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10",
                "sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10"
            ],
        ]

        epoch = "10"
        batch_size = batch_size
        dropout = "0.2"
        shapes = [
            [36, 32, 1],
            [36, 64, 32, 1],
            [36, 64, 64, 1],
            [36, 64, 64, 32, 1],
            [36, 64, 128, 64, 32, 1],
            [36, 128, 128, 64, 32 ,1],
            [36, 64, 128, 128, 32, 1],
            [36, 64, 128, 128, 64, 32, 1],
            [36, 64, 128, 256, 128, 64, 32, 1],
            [36, 64, 128, 256, 256, 64, 32, 1],
        ]

        for analysis_type_name, analysis_type in experiments:
            print(f"Analyzing {analysis_type_name}")
            experiment_dir = out_dir / self.subject_name / f"analysis/ml/{analysis_type_name}"
            if not experiment_dir.exists():
                experiment_dir.mkdir(parents=True, exist_ok=True)
            
            results_csv = experiment_dir / "results.csv"
            results = {}

            if not results_csv.exists():
                if analysis_type_name not in results:
                    results[analysis_type_name] ={}
                    results[analysis_type_name]["self"] = {"acc5": [], "acc10": []}
                    results[analysis_type_name]["test"] = {"acc5": [], "acc10": []}

                shape_cnt = 1
                for shape in shapes:
                    shape_name = f"shape{shape_cnt}"
                    shape_cnt += 1
                    print(f"\n\n\t >> Analyzing {shape_name}")

                    project_name = f"{analysis_type_name}/{shape_name}"
                    project_out_dir = out_dir / self.subject_name / "analysis/ml" / project_name

                    # train
                    cmd = [
                        "python3", "machine_learning.py",
                        "--subject", self.subject_name,
                        "--experiment-name", self.experiment_name,
                        "--targeting-experiment-name", analysis_type_name,
                        "--project-name", project_name,
                        "--train",
                        "--train-validate-test-ratio", "8", "1", "1",
                        "--random-seed", "42",
                        "--epoch", epoch,
                        "--batch-size", batch_size,
                        "--device", "cuda",
                        "--dropout", dropout,
                        "--model-shape", *map(str, shape),
                    ]
                    print(f"\t\t>>> training {project_name} with {shape}")
                    sp.run(cmd, cwd=src_dir, check=True, stdout=sp.PIPE)

                    # test self
                    cmd = [
                        "python3", "machine_learning.py",
                        "--subject", self.subject_name,
                        "--experiment-name", self.experiment_name,
                        "--targeting-experiment-name", analysis_type_name,
                        "--inference-name", "self",
                        "--inference",
                        "--model-name", f"{self.subject_name}::{project_name}",
                        "--device", "cuda"
                    ]
                    print(f"\t\t>>> testing on self {project_name} with {shape}")
                    sp.run(cmd, cwd=src_dir, check=True, stdout=sp.PIPE)

                    acc5, acc10 = self.get_mlp_acc_results(project_out_dir, "self")

                    # test opencv_calib3d_TF_top30
                    cmd = [
                        "python3", "machine_learning.py",
                        "--subject", "opencv_calib3d_TF_top30",
                        "--experiment-name", self.experiment_name,
                        "--targeting-experiment-name", "allfails-maxMutants-excludeCCT",
                        "--inference-name", "opencv_calib3d-D0",
                        "--inference",
                        "--model-name", f"{self.subject_name}::{project_name}",
                        "--device", "cuda"
                    ]
                    print(f"\t\t>>> testing on opencv_calib3d_TF_top30 {project_name} with {shape}")
                    sp.run(cmd, cwd=src_dir, check=True, stdout=sp.PIPE)

                    acc5, acc10 = self.get_mlp_acc_results(project_out_dir, "opencv_calib3d-D0")
                    results[analysis_type_name]["test"]["acc5"].append(acc5)
                    results[analysis_type_name]["test"]["acc10"].append(acc10)

                    acc5, acc10 = self.get_mlp_acc_results(project_out_dir, "self")
                    results[analysis_type_name]["self"]["acc5"].append(acc5)
                    results[analysis_type_name]["self"]["acc10"].append(acc10)
                
                with open(experiment_dir / "results.csv", "w") as f:
                    f.write("analysis_type,shape,test_acc5,test_acc10,self_acc5,self_acc10\n")
                    for analysis_type_name, data in results.items():
                        for i, shape in enumerate(shapes):
                            shape_name = f"shape{i+1}"
                            test_acc5 = data["test"]["acc5"][i]
                            test_acc10 = data["test"]["acc10"][i]
                            self_acc5 = data["self"]["acc5"][i]
                            self_acc10 = data["self"]["acc10"][i]
                            f.write(f"{analysis_type_name},{shape_name},{test_acc5},{test_acc10},{self_acc5},{self_acc10}\n")
            else:
                with open(results_csv, "r") as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        analysis_type_name = row[0]
                        shape = row[1]
                        test_acc5 = float(row[2])
                        test_acc10 = float(row[3])
                        self_acc5 = float(row[4])
                        self_acc10 = float(row[5])

                        if analysis_type_name not in results:
                            results[analysis_type_name] = {}
                            results[analysis_type_name]["test"] = {"acc5": [], "acc10": []}
                            results[analysis_type_name]["self"] = {"acc5": [], "acc10": []}

                        results[analysis_type_name]["test"]["acc5"].append(test_acc5)
                        results[analysis_type_name]["test"]["acc10"].append(test_acc10)
                        results[analysis_type_name]["self"]["acc5"].append(self_acc5)
                        results[analysis_type_name]["self"]["acc10"].append(self_acc10)

            # plot the results
            self.plot_results(experiment_dir, results, shapes)
    
    def plot_results(self, experiment_dir, results, shapes):
        """
        Plot the results
        """
        plt.figure(figsize=(8, 6))
        plt.ylim(0.0, 1.0)

        shape_names = [f"shape{i+1}" for i in range(len(shapes))]
        plt.xticks(range(len(shapes)), shape_names)
        for analysis_type_name, data in results.items():
            plt.plot(shape_names, data["test"]["acc5"], marker="o", label=f"{analysis_type_name}-acc5")
            plt.plot(shape_names, data["test"]["acc10"], marker="o", label=f"{analysis_type_name}-acc10")
        plt.xlabel("Model Shapes")
        plt.ylabel("FL accuracy")
        plt.title("FL accuracy of different models")
        plt.legend()
        plt.grid(True)
        plt.savefig(experiment_dir / "FLacc-Mshapes.png")
        plt.close()
                    

    def get_mlp_acc_results(self, project_out_dir, inference_name):
        """
        Get MLP accuracy results
        """
        inference_dir = project_out_dir / "inference" / inference_name
        fl_acc_txt = inference_dir / "fl_acc.txt"

        with open(fl_acc_txt, "r") as f:
            lines = f.readlines()
            acc5 = float(lines[2].strip().split(": ")[-1])
            acc10 = float(lines[4].strip().split(": ")[-1])
        
        return acc5, acc10


    def analyze10(self):
        """
        [stage05] Analyze10: Add cosine similarity of passing TCs to failing TCs based on branch_cov_bit_seq
        """

        if not self.db.column_exists("tc_info", "similarity"):
            self.db.add_column("tc_info", "similarity REAL DEFAULT NULL")

        subjects = [
            "zlib_ng_exp1",
            "libxml2_exp1",
            "opencv_features2d_exp1",
            "opencv_imgproc_exp1",
            "opencv_core_exp1",
            "jsoncpp_exp1",
        ]

        experiment_name = "e1"

        for subject in subjects:
            print(f">> Analyzing {subject}")
            # 1. First get buggy line information from db
            bug_info_list = self.db.read(
                "bug_info",
                columns="bug_idx, version, num_failing_tcs, num_passing_tcs, num_ccts",
                conditions={
                    "subject": subject,
                    "experiment_name": experiment_name,
                    "mbfl": True
                }
            )

            print(f"\t>> Analyzing {len(bug_info_list)} bugs")

            for bug_data in tqdm(bug_info_list, desc=f"Analyzing {subject} bugs"):
                bug_idx = bug_data[0]
                version = bug_data[1]
                num_failing_tcs = bug_data[2]
                num_passing_tcs = bug_data[3]
                num_ccts = bug_data[4]
                total_num_tcs = num_failing_tcs + num_passing_tcs + num_ccts

                failing_tc_list = self.db.read(
                    "tc_info",
                    columns="tc_idx, tc_name, tc_result, branch_cov_bit_seq",
                    conditions={
                        "bug_idx": bug_idx,
                        "tc_result": "fail"
                    }
                )

                fail_bit_seq_list = [[int(bit) for bit in tc_info[3]] for tc_info in failing_tc_list]

                passing_tc_list = self.db.read(
                    "tc_info",
                    columns="tc_idx, tc_name, tc_result, branch_cov_bit_seq",
                    conditions={
                        "bug_idx": bug_idx,
                        "tc_result": "pass"
                    }
                )

                cct_list = self.db.read(
                    "tc_info",
                    columns="tc_idx, tc_name, tc_result, branch_cov_bit_seq",
                    conditions={
                        "bug_idx": bug_idx,
                        "tc_result": "cct"
                    }
                )

                target_tc_list = passing_tc_list + cct_list

                cosine_results = {}
                failing_np = np.array(fail_bit_seq_list)
                for tc_info in target_tc_list:
                    tc_idx, tc_name, tc_result, branch_cov_bit_seq = tc_info
                    bit_seq = [int(bit) for bit in branch_cov_bit_seq]
                    bit_seq = np.array(bit_seq).reshape(1, -1)
                    
                    similarities_sklearn = cosine_similarity(bit_seq, failing_np)
                    avg_similarity = np.mean(similarities_sklearn)
                    avg_similarity = float(avg_similarity)
                    cosine_results[tc_name] = avg_similarity

                    # update the db
                    self.db.update(
                        "tc_info",
                        set_values={"similarity": avg_similarity},
                        conditions={
                            "bug_idx": bug_idx,
                            "tc_idx": tc_idx,
                            "tc_name": tc_name
                        }
                    )

        print(">> Done!")

    def analyze11(self,):
        """
        [stage05] Analyze11: Count the TCs with branch coverage similarity
        """
        subjects = [
            "zlib_ng_exp1",
            "libxml2_exp1",
            "opencv_features2d_exp1",
            "opencv_imgproc_exp1",
            "opencv_core_exp1",
            "jsoncpp_exp1",
        ]

        experiment_name = "e1"

        withCCT = False
        tc_reduction_rate = 0.5

        results = {}
        for subject in subjects:
            print(f">> Analyzing {subject}")
            # 1. First get buggy line information from db
            bug_info_list = self.db.read(
                "bug_info",
                columns="bug_idx, num_failing_tcs, num_passing_tcs, num_ccts, num_total_tcs",
                conditions={
                    "subject": subject,
                    "experiment_name": experiment_name,
                    "mbfl": True
                }
            )

            results[subject] = {
                "num_passing_tcs": [],
                "top50_similarity_score": [],
                "sum_tc_execution_time": [],
                "num_failing_tcs": [],
                "num_ccts": [],
                "num_total_tcs": []
            }
            
            for bug_info in bug_info_list:
                bug_idx = bug_info[0]
                num_failing_tcs = bug_info[1]
                num_passing_tcs = bug_info[2]
                num_ccts = bug_info[3]
                num_total_tcs = bug_info[4]

                results[subject]["num_passing_tcs"].append(num_passing_tcs)
                results[subject]["num_failing_tcs"].append(num_failing_tcs)
                results[subject]["num_ccts"].append(num_ccts)
                results[subject]["num_total_tcs"].append(num_total_tcs)
            
                special_str = "AND (tc_result = 'pass'"
                if withCCT:
                    special_str += " OR tc_result = 'cct'"
                special_str += ")"
                special_str += " ORDER BY similarity DESC"

                passing_tcs = self.db.read(
                    "tc_info",
                    columns="tc_idx, tc_result, cov_bit_seq, similarity, tc_execution_time_duration, tc_name",
                    conditions={
                        "bug_idx": bug_idx
                    },
                    special=special_str
                )

                limit = int(len(passing_tcs) * tc_reduction_rate)
                if limit == 0:
                    limit = 1
                top50 = passing_tcs[:limit]
                top50_similarity_score = [float(tc[3]) for tc in top50]
                tc_execution_time = [float(tc[4]) for tc in top50]

                failing_tcs = self.db.read(
                    "tc_info",
                    columns="tc_idx, tc_result, cov_bit_seq, similarity, tc_execution_time_duration, tc_name",
                    conditions={
                        "bug_idx": bug_idx,
                        "tc_result": "fail"
                    }
                )

                tc_execution_time += [float(tc[4]) for tc in failing_tcs]

                # print(f"\t>> Bug {bug_idx}: {len(passing_tcs)} passing tcs, {len(top50)} top50 tcs")

                avg_top50_similarity_score = np.mean(top50_similarity_score)
                results[subject]["top50_similarity_score"].append(avg_top50_similarity_score)
                sum_tc_exec_time = np.sum(tc_execution_time)
                results[subject]["sum_tc_execution_time"].append(sum_tc_exec_time)
    
        tc_specs_csv = open(root_dir / "rq_results" / "tc_specs.csv", "w")
        tc_specs_csv.write("subject,num_passing_tcs,num_failing_tcs,num_ccts,num_total_tcs,top50_similarity_score,sum_tc_execution_time\n")

        for subject, data in results.items():
            subject_avg_num_passing_tcs = np.mean(data["num_passing_tcs"])
            subject_avg_num_failing_tcs = np.mean(data["num_failing_tcs"])
            subject_avg_num_ccts = np.mean(data["num_ccts"])
            subject_avg_num_total_tcs = np.mean(data["num_total_tcs"])

            subject_avg_top50_similarity_score = np.mean(data["top50_similarity_score"])
            subject_avg_sum_tc_execution_time = np.mean(data["sum_tc_execution_time"])
            
            tc_specs_csv.write(f"{subject},{subject_avg_num_passing_tcs},{subject_avg_num_failing_tcs},{subject_avg_num_ccts},{subject_avg_num_total_tcs},{subject_avg_top50_similarity_score},{subject_avg_sum_tc_execution_time}\n")

            
