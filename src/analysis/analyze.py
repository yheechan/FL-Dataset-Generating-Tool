from copy import deepcopy
import random
import subprocess as sp
import csv
import json
import math
import pandas as pd
import matplotlib.pyplot as plt
import shutil

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


    def run(self, analysis_criteria, type_name=None):
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
        [stage05] analyze02: Analyze MBFL results
            for all buggy versions resulting from MBFL feature extraction
        """
        self.subject_out_dir = out_dir / self.subject_name
        self.analysis_dir = self.subject_out_dir / "analysis"

        self.type_dir = self.analysis_dir / type_name
        
        self.features_dir = self.type_dir / "fl_features"
        self.features_dir.mkdir(parents=True, exist_ok=True)


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
        
        # For each buggy version with MBFL feature
        mbfl_overal_data_json = self.type_dir / "mbfl_overall_data.json"
        if not mbfl_overal_data_json.exists():
            overall_data = {}
            for buggy_version in tqdm(target_buggy_version_list, desc=f"Analyzing buggy versions for MBFL ({type_name})"):
                bug_idx = buggy_version[0]
                version = buggy_version[1]
                num_failing_tcs = buggy_version[6]
                num_passing_tcs = buggy_version[7]
                num_ccts = buggy_version[8]
                num_total_lines = buggy_version[9]
                num_lines_executed_by_failing_tcs = buggy_version[10]
                self.reset_line_info_table(bug_idx, self.db)

                # For this buggy version calculate SBFL scores
                # write sbfl suspiciousness to line_info table
                line2spectrum = get_spectrum(bug_idx, self.db)
                line2sbfl = measure_sbfl_scores(line2spectrum, num_failing_tcs, num_passing_tcs, num_ccts, self.experiment.analysis_config["include_cct"])
                update_line_info_table_with_sbfl_scores(bug_idx, line2sbfl, self.db)

                # Get lines that we target to analyze for MBFL
                target_line_idx = self.get_target_line_idx(
                    bug_idx, num_total_lines,
                    self.experiment.analysis_config["line_selection_rate"],
                    self.experiment.analysis_config["mbfl_method"],
                    num_lines_executed_by_failing_tcs
                )
                target_line_idx_copied = deepcopy(target_line_idx)

                # map line_idx to line_info map
                line_idx2line_info = {}
                for row in target_line_idx_copied:
                    line_idx = row[0]
                    line_idx2line_info[line_idx] = {
                        "file": row[1],
                        "function": row[2],
                        "lineno": row[3]
                    }

                debug_print(self.verbose, f">> Selected {len(line_idx2line_info)} lines for MBFL analysis")

                # Get all mutants generated on target lines
                lines_idx2mutant_idx = get_mutations_on_target_lines(bug_idx, line_idx2line_info, self.db)
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
                                "lineno": row[3]
                            }

                        version_data = self.analyze_bug_version_for_mbfl(
                            line_idx2line_info, lines_idx2mutant_idx,
                            buggy_version, target_line_idx_copied, mtc, iter_num
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
    def get_target_line_idx(self, bug_idx, num_total_lines, line_selection_rate, mbfl_method, num_lines_executed_by_failing_tcs):
        """
        Get target line index for MBFL analysis
        """
        if mbfl_method == "all_fails":
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                }
            )
        elif mbfl_method == "rand":
            rand_num = int(num_lines_executed_by_failing_tcs * line_selection_rate)
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                },
                special=f"ORDER BY RANDOM() LIMIT {rand_num}"
            )
        elif mbfl_method == "sbfl":
            sbfl_num = int(num_lines_executed_by_failing_tcs * line_selection_rate)
            sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                },
                special=f"ORDER BY {sbfl_standard} DESC LIMIT {sbfl_num}"
            )
        elif mbfl_method == "sbfl-test":
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    "selected_for_mbfl": True
                }
            )
        
        return target_line_idx

    def analyze_bug_version_for_mbfl(self,
                                     line_idx2line_info, lines_idx2mutant_idx,
                                     buggy_version, target_line_idx_copied, mtc, iter_num):
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
        total_num_of_failing_tcs = num_failing_tcs

        debug_print(self.verbose, f">> Analyzing {bug_idx} {version} ({buggy_file}::{buggy_function}::{buggy_lineno})")
        debug_print(self.verbose, f">> Total number of failing test cases: {total_num_of_failing_tcs}")

        target_line_idx = target_line_idx_copied
        
        debug_print(self.verbose, f">> Selected {len(target_line_idx)} lines for MBFL analysis")
        # print(f">> Selected {len(target_line_idx)} lines for MBFL analysis")
        

        # Measure MBFL score for targetted lines
        mtc_version_data = measure_mbfl_scores(
            line_idx2line_info,
            lines_idx2mutant_idx,
            total_num_of_failing_tcs,
            mtc,
            self.experiment.analysis_config
        )
        mtc_version_data["total_num_of_failing_tcs"] = total_num_of_failing_tcs

        # Update line_info table with met_score, muse_score
        update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx, self.db)

        # This means the last iteration of the last mtc
        if mtc == self.experiment.analysis_config["mut_cnt_config"][-1] \
            and iter_num == self.experiment.analysis_config["experiment_repeat"] - 1:
            
            if self.experiment.analysis_config["apply_heuristic"]:
                buggy_line_f2p = 0
                if buggy_line_idx not in lines_idx2mutant_idx:
                    if version not in self.experiment.analysis_config["versions_to_remove"]:
                        self.experiment.analysis_config["versions_to_remove"].append(version)
                else:
                    for buggy_line_mutants in lines_idx2mutant_idx[buggy_line_idx]:
                        buggy_line_f2p += buggy_line_mutants["f2p"]
                    if buggy_line_f2p == 0:
                        if version not in self.experiment.analysis_config["versions_to_remove"]:
                            self.experiment.analysis_config["versions_to_remove"].append(version)
                
            # save fl features to csv
            self.save_fl_features_to_csv(bug_idx, version)
        
        # Measure rank of buggy line
        rank_data = self.measure_buggy_line_rank(bug_idx, buggy_file, buggy_function)
        self.reset_line_info_table(bug_idx, self.db)

        version_data = {
            "bug_idx": bug_idx,
            "version": version,
            "buggy_file": buggy_file,
            "buggy_function": buggy_function,
            "buggy_lineno": buggy_lineno
        }
        total_data = {**version_data, **mtc_version_data, **rank_data}
        return total_data

    def reset_line_info_table(self, bug_idx, db):
        """
        Reset line_info table for next iteration
        """
        values = {
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

    def save_fl_features_to_csv(self, bug_idx, version):
        """
        Save FL features to csv file
        """
        fl_features = ["ep", "ef", "np", "nf"]
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            fl_features.extend(sub_form_list)
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            fl_features.extend(sub_form_list)

        features = ["file", "function", "lineno", "is_buggy_line"] + fl_features

        if self.experiment.analysis_config["include_cct"]:
            features.extend(["cct_ep, cct_np"])

        features_str = ", ".join(features)
        rows = self.db.read(
            "line_info",
            columns=features_str,
            conditions={"bug_idx": bug_idx}
        )

        if self.experiment.analysis_config["include_cct"]:
            for row in rows:
                cct_ep, cct_ef = row[-2:]
                row[4] += cct_ep
                row[5] += cct_ef
                row = row[:-2]
            features = features[:-2]


        with open(self.features_dir / f"{version}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(features)
            for row in rows:
                writer.writerow(row)
    
    def measure_buggy_line_rank(self, bug_idx, buggy_file, buggy_function):
        """
        Measure rank of buggy line
        """

        # Step 1: getch relevant information
        columns = ["file", "function", "met_3", "muse_6"]
        col_str = ", ".join(columns)
        rows = self.db.read(
            "line_info",
            columns=col_str,
            conditions={"bug_idx": bug_idx}
        )


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
        [stage06] analyze03: Analyze probability that buggy line
            is within top-k percent based on sbfl suspiciousness
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
                bug_idx, num_total_lines,
                self.experiment.analysis_config["line_selection_rate"],
                self.experiment.analysis_config["mbfl_method"],
                num_lines_executed_by_failing_tcs
            )

            top_line_idx_list = [line_idx[0] for line_idx in target_line_idx]

            # Get top-k percent of lines based on sbfl suspiciousness
            if self.experiment.analysis_config["mbfl_method"] == "sbfl-test":
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

        if self.experiment.analysis_config["mbfl_method"] == "sbfl-test":
            avg_sbfl_selected_rate = sum(sbfl_selected_rate) / len(sbfl_selected_rate)
            print(f"Average SBFL selected rate: {avg_sbfl_selected_rate}")

    def analyze04(self):
        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        # "bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)

        # For each buggy version with MBFL feature
        rank_dataset = []
        acc_5_list = []
        acc10_list = []
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

            rank_data = self.measure_sbfl_rank(bug_idx, buggy_file, buggy_function)
            rank_dataset.append(rank_data["sbfl_rank"])

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

        print(f"Accuracy@5: {acc_5}")
        print(f"Accuracy@10: {acc_10}")
        
        average_rank = sum(rank_dataset) / len(rank_dataset)
        print(f"Average SBFL rank {self.experiment.analysis_config['sbfl_standard']}: {average_rank}")

    def measure_sbfl_rank(self, bug_idx, buggy_file, buggy_function):
        sbfl_standard = self.experiment.analysis_config["sbfl_standard"]
        rank_name = f"{sbfl_standard}_rank"
        # Step 1: getch relevant information
        columns = ["file", "function", sbfl_standard]
        col_str = ", ".join(columns)
        rows = self.db.read(
            "line_info",
            columns=col_str,
            conditions={"bug_idx": bug_idx}
        )


        # Step2: Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows, columns=columns)
        grouped = df.groupby(["file", "function"]).agg(
            sbfl_score=(sbfl_standard, "max"),
        ).reset_index()
        # Step 4: Assign ranks based on met_score descening, with tie-braking rules
        grouped[rank_name] = grouped["sbfl_score"].rank(method="max", ascending=False).astype(int)

        # Save to tmp.csv
        # grouped.to_csv("tmp.csv", index=False)

        # Step 5: Get rank of buggy line by buggy_file, buggy_function
        buggy_line_rank = grouped[
            (grouped["file"] == buggy_file) & (grouped["function"] == buggy_function)
        ][[rank_name]]


        rank = buggy_line_rank[rank_name].values[0]

        total_number_of_functions = len(grouped)

        rank_data = {
            "sbfl_rank": rank,
            "total_number_of_functions": total_number_of_functions
        }

        return rank_data
    
    def analyze05(self):
        """
        [stage07] analyze05: Analyze SBFL statistics
            for all buggy versions resulting from SBFL feature extraction
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
        """
        Download SBFL statistics for a single buggy version
        """
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


