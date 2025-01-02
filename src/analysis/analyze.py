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

from lib.experiment import Experiment
from lib.database import CRUD
from lib.config import set_seed
from tqdm import tqdm


MBFL_METHOD = "for_random_mbfl"
# MBFL_METHOD = "for_sbfl_ranked_mbfl_desc"
MAX_LINES_FOR_RANDOM = 50
SBFL_RANKED_RATE = 0.30
SBFL_STANDARD = "gp13"
MUT_CNT_CONFIG = [2, 6,10]
EXPERIMENT_REPEAT = 5
INCLUDE_CCT = False
APPLY_HEURISTIC = False
VERSIONS_TO_REMOVE = []
        

class Analyze:
    def __init__(
            self, subject_name, experiment_name, verbose=False,
        ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name
        self.verbose = verbose

        self.subject_out_dir = out_dir / self.subject_name

        self.experiment = Experiment()
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
        target_buggy_version_list = self.get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl")

        
        # For each buggy version with MBFL feature
        mbfl_overal_data_json = self.type_dir / "mbfl_overall_data.json"
        if not mbfl_overal_data_json.exists():
            overall_data = {}
            for mtc in MUT_CNT_CONFIG:
                overall_data[mtc] = {}
                

                for buggy_version in tqdm(target_buggy_version_list, desc=f"Analyzing buggy versions for mtc={mtc}"):
                    # version_data consists of:
                    #   - bug_idx
                    #   - version
                    #   - buggy_file
                    #   - buggy_function
                    #   - buggy_lineno
                    #   - total_num_of_failing_tcs
                    #   - total_num_of_utilized_mutants
                    #   - total_build_time
                    #   - total_tc_execution_time
                    #   - met_rank
                    #   - muse_rank
                    #   - total_number_of_functions
                    for iter_num in range(EXPERIMENT_REPEAT):
                        version_data = self.analyze_bug_version_for_mbfl(buggy_version, mtc)
                        if version_data["version"] not in overall_data[mtc]:
                            overall_data[mtc][version_data["version"]] = []
                        overall_data[mtc][version_data["version"]].append(version_data)
        else:
            with open(mbfl_overal_data_json, "r") as f:
                overall_data = json.load(f)
        
        if APPLY_HEURISTIC:
            print(f"Versions to remove: {len(VERSIONS_TO_REMOVE)}")
            for version in VERSIONS_TO_REMOVE:
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
            
            for iter_cnt in range(EXPERIMENT_REPEAT):
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
                for iter_cnt in range(EXPERIMENT_REPEAT):
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
            json.dump({
                "MBFL_METHOD": MBFL_METHOD,
                "MAX_LINES_FOR_RANDOM": MAX_LINES_FOR_RANDOM,
                "SBFL_RANKED_RATE": SBFL_RANKED_RATE,
                "SBFL_STANDARD": SBFL_STANDARD,
                "MUT_CNT_CONFIG": MUT_CNT_CONFIG,
                "EXPERIMENT_REPEAT": EXPERIMENT_REPEAT,
                "INCLUDE_CCT": INCLUDE_CCT,
                "APPLY_HEURISTIC": APPLY_HEURISTIC,
                "VERSIONS_TO_REMOVE": VERSIONS_TO_REMOVE
            }, f, indent=2)
        
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

        debug_print(self.verbose, f">> Analyzing {bug_idx} {version} ({buggy_file}::{buggy_function}::{buggy_lineno})")

        total_num_of_failing_tcs = self.get_total_number_of_failing_tcs(bug_idx)
        debug_print(self.verbose, f">> Total number of failing test cases: {total_num_of_failing_tcs}")

        # THIS IS TEMPORARY
        # Get lines that we target to analyze for MBFL
        if MBFL_METHOD == "for_random_mbfl":
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    MBFL_METHOD: True
                },
                special=f"ORDER BY line_idx LIMIT {MAX_LINES_FOR_RANDOM}"
            )
        else:
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    MBFL_METHOD: True
                },
                # special=f"ORDER BY {SBFL_STANDARD} LIMIT {num_lines_for_random}"
                special=f"ORDER BY {SBFL_STANDARD}"
            )
        
        debug_print(self.verbose, f">> Selected {len(target_line_idx)} lines for MBFL analysis")
        # print(f">> Selected {len(target_line_idx)} lines for MBFL analysis")
        
        # map line_idx to line_info map
        line_idx2line_info = {}
        for row in target_line_idx:
            line_idx = row[0]
            line_idx2line_info[line_idx] = {
                "file": row[1],
                "function": row[2],
                "lineno": row[3]
            }

        # Make sure to add buggy line to line_idx2line_info
        if buggy_line_idx not in line_idx2line_info:
            # remove randomly one line_idx in line_idx2line_info dict
            key_list = list(line_idx2line_info.keys())
            random.shuffle(key_list)
            line_idx2line_info.pop(key_list[0])

            line_idx2line_info[buggy_line_idx] = {
                "file": buggy_file,
                "function": buggy_function,
                "lineno": buggy_lineno
            }
        
        assert buggy_line_idx in line_idx2line_info, f"buggy_line_idx {buggy_line_idx} not in line_idx2line_info"

        debug_print(self.verbose, f">> Selected {len(line_idx2line_info)} lines for MBFL analysis")

        # Get all mutants generated on target lines
        lines_idx2mutant_idx = self.get_mutations_on_target_lines(bug_idx, line_idx2line_info)
        debug_print(self.verbose, f">> Found {len(lines_idx2mutant_idx)} mutants on target lines")

        if APPLY_HEURISTIC and mtc == MUT_CNT_CONFIG[-1]:
            buggy_line_f2p = 0
            if buggy_line_idx not in lines_idx2mutant_idx:
                VERSIONS_TO_REMOVE.append(version)
            else:
                for buggy_line_mutants in lines_idx2mutant_idx[buggy_line_idx]:
                    buggy_line_f2p += buggy_line_mutants["f2p"]
                if buggy_line_f2p == 0:
                    VERSIONS_TO_REMOVE.append(version)

        # Measure MBFL score for targetted lines
        mtc_version_data = self.measure_mbfl_scores(line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc)
        mtc_version_data["total_num_of_failing_tcs"] = total_num_of_failing_tcs

        # Update line_info table with met_score, muse_score
        self.update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx)

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
        

    
    def update_line_info_table_with_mbfl_scores(self, bug_idx, line_idx2line_info, lines_idx2mutant_idx):
        """
        Update line_info table with MBFL scores
        """
        for line_idx, line_info in line_idx2line_info.items():
            if line_idx not in lines_idx2mutant_idx:
                continue

            met_score = line_info["met_score"]
            muse_score = line_info["muse_score"]
            # print(f"BUG: {bug_idx}, Line {line_idx} - Metallaxis: {met_score}, MUSE: {muse_score}")
            
            self.db.update(
                "line_info",
                set_values={
                    "met_score": met_score,
                    "muse_score": muse_score
                },
                conditions={
                    "bug_idx": bug_idx,
                    "line_idx": line_idx
                }
            )


    
    def measure_mbfl_scores(self, line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc):
        """
        Measure MBFL scores for a given number of mutants
        """
        debug_print(self.verbose, f">> Measuring MBFL scores for number of mutation setting to {mtc}")

        # Select mtc mutants per line at random
        utilizing_line_idx2mutants, total_num_of_utilized_mutants = self.select_random_mtc_mutants_per_line(lines_idx2mutant_idx, mtc)

        # Calculate total information
        total_p2f, total_f2p, \
            total_build_time, total_tc_execution_time \
            = self.calculate_total_info(utilizing_line_idx2mutants)


        for line_idx, mutants in utilizing_line_idx2mutants.items():
            # print(f"Analyzing line {line_idx}")

            met_data = self.measure_metallaxis(mutants, total_num_of_failing_tcs)
            muse_data = self.measure_muse(mutants, total_p2f, total_f2p)

            # met_score, muse_score = met_data["met_score"], muse_data["muse_score"]
            # print(f"\tMetallaxis score: {met_score}")
            # print(f"\tMUSE score: {muse_score}")

            line_idx2line_info[line_idx]["met_score"] = met_data["met_score"]
            line_idx2line_info[line_idx]["muse_score"] = muse_data["muse_score"]
        
        mtc_version_data = {
            "total_num_of_utilized_mutants": total_num_of_utilized_mutants,
            "total_build_time": total_build_time,
            "total_tc_execution_time": total_tc_execution_time
        }

        return  mtc_version_data
    
    def measure_metallaxis(self, mutants, total_num_of_failing_tcs):
        """
        Measure Metallaxis score
        """
        met_score_list = []

        for mutant in mutants:
            f2p = mutant["f2p"]
            p2f = mutant["p2f"]
            if INCLUDE_CCT:
                p2f += mutant["p2f_cct"]
            
            score = 0.0
            if f2p + p2f == 0.0:
                score = 0.0
            else:
                score = ((f2p) / math.sqrt(total_num_of_failing_tcs * (f2p + p2f)))
            
            met_score_list.append(score)
        
        if len(met_score_list) == 0:
            return {
                "total_num_of_failing_tcs": total_num_of_failing_tcs,
                "met_score": 0.0
            }

        final_met_score = max(met_score_list)
        met_data = {
            "total_num_of_failing_tcs": total_num_of_failing_tcs,
            "met_score": final_met_score
        }
        return met_data
    

    def measure_muse(self, mutants, total_p2f, total_f2p):
        utilized_mutant_cnt = len(mutants)
        line_total_p2f = 0
        line_total_f2p = 0

        final_muse_score = 0.0

        for mutant in mutants:
            line_total_p2f += mutant["p2f"]
            line_total_f2p += mutant["f2p"]
            if INCLUDE_CCT:
                line_total_p2f += mutant["p2f_cct"]
        
        muse_1 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1)))
        muse_2 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1)))

        muse_3 = muse_1 * line_total_f2p
        muse_4 = muse_2 * line_total_p2f

        final_muse_score = muse_3 - muse_4

        muse_data = {
            "utilized_mutant_cnt": utilized_mutant_cnt,
            "total_f2p": total_f2p,
            "total_p2f": total_p2f,
            "line_total_f2p": line_total_f2p,
            "line_total_p2f": line_total_p2f,
            "muse_1": muse_1,
            "muse_2": muse_2,
            "muse_3": muse_3,
            "muse_4": muse_4,
            "muse_score": final_muse_score
        }

        return muse_data




    
    def calculate_total_info(self, utilizing_line_idx2mutants):
        """
        Calculate total information for selected mutants
            - total_p2f, total_f2p, total_build_time, total_tc_execution_time
        """

        total_p2f = 0
        total_f2p = 0
        total_build_time = 0
        total_tc_execution_time = 0

        for line_idx, mutants in utilizing_line_idx2mutants.items():
            for mutant in mutants:
                total_p2f += mutant["p2f"]
                total_f2p += mutant["f2p"]
                total_build_time += mutant["build_time_duration"]
                total_tc_execution_time += mutant["tc_execution_time_duration"]
                if INCLUDE_CCT:
                    total_p2f += mutant["p2f_cct"]
                    total_tc_execution_time += mutant["ccts_execution_time_duration"]

        return total_p2f, total_f2p, total_build_time, total_tc_execution_time


    def select_random_mtc_mutants_per_line(self, lines_idx2mutant_idx, mtc):
        """
        Select mtc mutants per line at random
        """
        selected_mutants = {}
        total_num_of_utilized_mutants = 0
        for line_idx in lines_idx2mutant_idx:
            mutants = lines_idx2mutant_idx[line_idx]
            random.shuffle(mutants)
            selected_mutants[line_idx] = []
            for mutant in mutants:
                if len(selected_mutants[line_idx]) == mtc:
                    break
                if mutant["build_result"] == False:
                    continue
                selected_mutants[line_idx].append(mutant)
                total_num_of_utilized_mutants += 1
        return selected_mutants, total_num_of_utilized_mutants
        

    def get_total_number_of_failing_tcs(self, bug_idx):
        """
        Get total number of failing test cases for a bug_idx
        """
        num_failing_tcs = self.db.read(
            "bug_info",
            columns="num_failing_tcs",
            conditions={"bug_idx": bug_idx}
        )
        return num_failing_tcs[0][0]

    def get_target_buggy_version_list(self, subject_name, experiment_name, stage):
        """
        Get list of buggy versions that meet the criteria
        """
        return self.db.read(
            "bug_info",
            columns="bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
            conditions={
                "subject": subject_name,
                "experiment_name": experiment_name,
                stage: True
            }
        )
    
    def get_mutations_on_target_lines(self, bug_idx, line_idx2line_info):
        """
        Get mutations on target lines
        """
        columns = [
            "line_idx", "mutant_idx", "build_result",
            "f2p", "p2f", "f2f", "p2p", "p2f_cct", "p2p_cct",
            "build_time_duration", "tc_execution_time_duration", "ccts_execution_time_duration"
        ]
        col_str = ", ".join(columns)
        special_str = f"AND line_idx IN ({', '.join([str(line_idx) for line_idx in line_idx2line_info])})"
        ret = self.db.read(
            "mutation_info",
            columns=col_str,
            conditions={
                "bug_idx": bug_idx,
                "is_for_test": True
            },
            special=special_str
        )


        # Map line_idx to mutant_idx
        lines_idx2mutant_idx = {}
        for row in ret:
            line_idx = row[0]
            if line_idx not in lines_idx2mutant_idx:
                lines_idx2mutant_idx[line_idx] = []
            lines_idx2mutant_idx[line_idx].append(
                {
                    "mutant_idx": row[1],
                    "build_result": row[2],
                    "f2p": row[3],
                    "p2f": row[4],
                    "f2f": row[5],
                    "p2p": row[6],
                    "p2f_cct": row[7],
                    "p2p_cct": row[8],
                    "build_time_duration": row[9],
                    "tc_execution_time_duration": row[10],
                    "ccts_execution_time_duration": row[11]
                }
            )
        
        return lines_idx2mutant_idx
    

    def analyze03(self):
        """
        [stage06] analyze03: Analyze probability that buggy line
            is within top-k percent based on sbfl suspiciousness
        """

        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        # "bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx",
        target_buggy_version_list = self.get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl")

        # For each buggy version with MBFL feature
        within_top_idx = 0
        within_bot_idx = 0
        for buggy_version in tqdm(target_buggy_version_list, desc="Analyzing buggy versions for MBFL"):
            bug_idx, version, buggy_file, buggy_function, buggy_lineno, buggy_line_idx = buggy_version

            # First get number of lines for the bug_idx
            num_lines = self.db.read(
                "line_info",
                columns="COUNT(line_idx)",
                conditions={"bug_idx": bug_idx}
            )

            num_lines = num_lines[0][0]
            num_lines_for_random = int(num_lines * SBFL_RANKED_RATE)

            top_line_idx_list = self.db.read(
                "line_info",
                columns="line_idx",
                conditions={
                    "bug_idx": bug_idx,
                },
                special=f"ORDER BY {SBFL_STANDARD} DESC LIMIT {num_lines_for_random}"
            )
            top_line_idx_list = [line_idx[0] for line_idx in top_line_idx_list]

            bot_line_idx_list = self.db.read(
                "line_info",
                columns="line_idx",
                conditions={
                    "bug_idx": bug_idx,
                },
                special=f"ORDER BY {SBFL_STANDARD} ASC LIMIT {num_lines_for_random}"
            )
            bot_line_idx_list = [line_idx[0] for line_idx in bot_line_idx_list]

            if buggy_line_idx in top_line_idx_list:
                within_top_idx += 1
            if buggy_line_idx in bot_line_idx_list:
                within_bot_idx += 1
            
        probability_within_top = within_top_idx / len(target_buggy_version_list)
        probability_within_bot = within_bot_idx / len(target_buggy_version_list)

        print(f"Probability that buggy line is within top-{SBFL_RANKED_RATE * 100}%: {probability_within_top}")
        print(f"Probability that buggy line is within bot-{SBFL_RANKED_RATE * 100}%: {probability_within_bot}")

