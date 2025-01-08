from copy import deepcopy
import random
import subprocess as sp
import csv
import json
import math
import pandas as pd
import matplotlib.pyplot as plt

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

        self.subject_out_dir = out_dir / self.subject_name
        self.analysis_dir = self.subject_out_dir / "analysis"
        self.analysis_dir.mkdir(exist_ok=True, parents=True)

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
        self.type_dir = self.analysis_dir / type_name
        self.type_dir.mkdir(exist_ok=True, parents=True)

        # add muse_score, met_score on line_info table
        if not self.db.column_exists("line_info", "muse_score"):
            self.db.add_column("line_info", "muse_score FLOAT DEFAULT 0.0")
        if not self.db.column_exists("line_info", "met_score"):
            self.db.add_column("line_info", "met_score FLOAT DEFAULT 0.0")


        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        target_buggy_version_list = get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl", self.db)

        
        # For each buggy version with MBFL feature
        mbfl_overal_data_json = self.type_dir / "mbfl_overall_data.json"
        if not mbfl_overal_data_json.exists():
            overall_data = {}
            for mtc in self.experiment.analysis_config["mut_cnt_config"]:
                overall_data[mtc] = {}
                

                for buggy_version in tqdm(target_buggy_version_list, desc=f"Analyzing buggy versions for mtc={mtc}"):
                    for iter_num in range(self.experiment.analysis_config["experiment_repeat"]):
                        version_data = self.analyze_bug_version_for_mbfl(buggy_version, mtc)
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
    def analyze_bug_version_for_mbfl(self, buggy_version, mtc):
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
        
        debug_print(self.verbose, f">> Selected {len(target_line_idx)} lines for MBFL analysis")
        # print(f">> Selected {len(target_line_idx)} lines for MBFL analysis")

        if self.experiment.analysis_config["deliberate_inclusion"]:
            # Make sure to add buggy line to target_line_idx
            if buggy_line_idx not in [row[0] for row in target_line_idx]:
                target_line_idx.append((buggy_line_idx, buggy_file, buggy_function, buggy_lineno))
        
        # map line_idx to line_info map
        line_idx2line_info = {}
        for row in target_line_idx:
            line_idx = row[0]
            line_idx2line_info[line_idx] = {
                "file": row[1],
                "function": row[2],
                "lineno": row[3]
            }

        debug_print(self.verbose, f">> Selected {len(line_idx2line_info)} lines for MBFL analysis")

        # Get all mutants generated on target lines
        lines_idx2mutant_idx = get_mutations_on_target_lines(bug_idx, line_idx2line_info, self.db)
        debug_print(self.verbose, f">> Found {len(lines_idx2mutant_idx)} mutants on target lines")

        if self.experiment.analysis_config["apply_heuristic"] and mtc == self.experiment.analysis_config["mut_cnt_config"][-1]:
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

        # Measure rank of buggy line
        rank_data = self.measure_buggy_line_rank(bug_idx, buggy_file, buggy_function)

        version_data = {
            "bug_idx": bug_idx,
            "version": version,
            "buggy_file": buggy_file,
            "buggy_function": buggy_function,
            "buggy_lineno": buggy_lineno
        }
        total_data = {**version_data, **mtc_version_data, **rank_data}
        return total_data
    
    def measure_buggy_line_rank(self, bug_idx, buggy_file, buggy_function):
        """
        Measure rank of buggy line
        """

        # Step 1: getch relevant information
        columns = ["file", "function", "met_score", "muse_score"]
        col_str = ", ".join(columns)
        rows = self.db.read(
            "line_info",
            columns=col_str,
            conditions={"bug_idx": bug_idx}
        )

        # Step2: Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows, columns=columns)
        grouped = df.groupby(["file", "function"]).agg(
            met_score=("met_score", "max"),
            muse_score=("muse_score", "max")
        ).reset_index()

        # Step 4: Assign ranks based on met_score descening, with tie-braking rules
        grouped["met_rank"] = grouped["met_score"].rank(method="max", ascending=False).astype(int)
        grouped["muse_rank"] = grouped["muse_score"].rank(method="max", ascending=False).astype(int)

        # Save to tmp.csv
        # grouped.to_csv("tmp.csv", index=False)

        # Step 5: Get rank of buggy line by buggy_file, buggy_function
        buggy_line_rank = grouped[
            (grouped["file"] == buggy_file) & (grouped["function"] == buggy_function)
        ][["met_rank", "muse_rank"]]

        met_rank = buggy_line_rank["met_rank"].values[0]
        muse_rank = buggy_line_rank["muse_rank"].values[0]

        total_number_of_functions = len(grouped)

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
            top_line_idx_list = [line_idx[0] for line_idx in target_line_idx]

            if buggy_line_idx in top_line_idx_list:
                buggy_lines_selected_cnt += 1
            
        probability_within_top = buggy_lines_selected_cnt / len(target_buggy_version_list)

        rate = self.experiment.analysis_config["sbfl_ranked_rate"] * 100
        print(f"Probability that buggy line is within top-{rate}%: {probability_within_top}")

