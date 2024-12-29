from copy import deepcopy
import random
import subprocess as sp
import csv
import json
import math

from lib.utils import *
from analysis.individual import Individual
from lib.experiment import Experiment
from analysis.rank_utils import *

from lib.experiment import Experiment
from lib.database import CRUD
from lib.config import set_seed


MBFL_METHOD = "for_random_mbfl"
# MBFL_METHOD = "for_sbfl_ranked_mbfl_desc"
MAX_LINES_FOR_RANDOM = 100
SBFL_RANKED_RATE = 0.30
SBFL_STANDARD = "gp13"
MUT_CNT_CONFIG = [2, 4, 6, 8, 10]
INCLUDE_CCT = False
        

class Analyze:
    def __init__(
            self, subject_name, experiment_name
        ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name

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

        # self.set_name = set_name
        # self.set_dir = out_dir / self.subject_name / self.set_name
        # self.individual_list = get_dirs_in_dir(self.set_dir)
        # self.set_size = len(self.individual_list)

        # self.stat_dir = stats_dir / self.subject_name
        # self.stat_dir.mkdir(exist_ok=True, parents=True)

        # if not output_csv.endswith(".csv"):
        #     output_csv += ".csv"
        # self.output_csv = self.stat_dir / output_csv
    
    def run(self, analysis_criteria):
        for ana_type in analysis_criteria:
            if ana_type == 1:
                self.analyze01()
            elif ana_type == 2:
                self.analyze02()


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
            "num_total_lines"
        ]
        col_str = ", ".join(columns)

        res = self.db.read(
            "bug_info",
            columns=col_str,
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name,
                "prerequisites": True
            }
        )

        columns.extend(["fail_line_cov", "pass_line_cov", "cct_line_cov", "total_line_cov"])

        analysis_result = {}
        total_result = {}
        for row in res:
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

        
        col_for_table = ["subject TEXT", "experiment_name TEXT"]
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


    def analyze02(self):
        """
        [stage05] analyze02: Analyze MBFL results
            for all buggy versions resulting from MBFL feature extraction
        """

        # add muse_score, met_score on line_info table
        if not self.db.column_exists("line_info", "muse_score"):
            self.db.add_column("line_info", "muse_score FLOAT DEFAULT NULL")
        if not self.db.column_exists("line_info", "met_score"):
            self.db.add_column("line_info", "met_score FLOAT DEFAULT NULL")


        # Step 1: retrieve list of bug_idx where mbfl is TRUE
        target_buggy_version_list = self.get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl")

        
        # For each buggy version with MBFL feature
        for buggy_version in target_buggy_version_list:
            self.analyze_bug_version_for_mbfl(buggy_version)
            break

    # +++++++++++++++++++++++
    # HELPER FUNCTIONS FOR ANALYZE02
    # +++++++++++++++++++++++
    def analyze_bug_version_for_mbfl(self, buggy_version):
        """
        Analyze a single buggy version for MBFL
        """
        bug_idx = buggy_version[0]
        version = buggy_version[1]
        buggy_file = buggy_version[2]
        buggy_function = buggy_version[3]
        buggy_lineno = buggy_version[4]
        self.buggy_line_idx = buggy_version[5]
        buggy_line_idx = buggy_version[5]

        print(f"Analyzing {bug_idx} {version} ({buggy_file}::{buggy_function}::{buggy_lineno})")

        total_num_of_failing_tcs = self.get_total_number_of_failing_tcs(bug_idx)
        print(f"Total number of failing test cases: {total_num_of_failing_tcs}")

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
                special=f"ORDER BY RANDOM() LIMIT {MAX_LINES_FOR_RANDOM}"
            )
        else:
            # First get number of lines for the bug_idx
            num_lines = self.db.read(
                "line_info",
                columns="COUNT(line_idx)",
                conditions={"bug_idx": bug_idx}
            )

            num_lines = num_lines[0][0]
            num_lines_for_random = int(num_lines * SBFL_RANKED_RATE)
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    MBFL_METHOD: True
                },
                special=f"ORDER BY {SBFL_STANDARD} LIMIT {num_lines_for_random}"
            )
        
        print(f"Selected {len(target_line_idx)} lines for MBFL analysis")
        
        # map line_idx to line_info map
        line_idx2line_info = {}
        for row in target_line_idx:
            line_idx = row[0]
            line_idx2line_info[line_idx] = {
                "file": row[1],
                "function": row[2],
                "lineno": row[3]
            }

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

        print(f"Selected {len(line_idx2line_info)} lines for MBFL analysis")

        # Get all mutants generated on target lines
        lines_idx2mutant_idx = self.get_mutations_on_target_lines(bug_idx, line_idx2line_info)
        print(f"Found {len(lines_idx2mutant_idx)} mutants on target lines")

        # measure mbfl scores
        for mtc in MUT_CNT_CONFIG:
            self.measure_mbfl_scores(line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc)
    
    def measure_mbfl_scores(self, line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc):
        """
        Measure MBFL scores for a given number of mutants
        """
        print(f"Measuring MBFL scores for number of mutation setting to {mtc}")

        # Select mtc mutants per line at random
        utilizing_line_idx2mutants = self.select_random_mtc_mutants_per_line(lines_idx2mutant_idx, mtc)

        # Calculate total information
        total_p2f, total_f2p, \
            total_build_time, total_tc_execution_time \
            = self.calculate_total_info(utilizing_line_idx2mutants)


        for line_idx, mutants in utilizing_line_idx2mutants.items():
            if line_idx != self.buggy_line_idx:
                continue
            print(f"Analyzing line {line_idx}")
            met_data = self.measure_metallaxis(mutants, total_num_of_failing_tcs)
            muse_data = self.measure_must_score(mutants, total_p2f, total_f2p)

            print(f"Metallaxis score: {met_data}")
            print(f"MUSE score: {muse_data}")

            break
    
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
            return 0.0
        final_met_score = max(met_score_list)
        met_data = {
            "total_num_of_failing_tcs": total_num_of_failing_tcs,
            "met susp score": final_met_score
        }
        return met_data
    

    def measure_must_score(self, mutants, total_p2f, total_f2p):
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
            "muse susp score": final_muse_score
        }

        return final_muse_score, muse_data




    
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
        return selected_mutants
        

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
            
        
    
    def usable_buggy_versions(self):
        csv_keys = [
            "buggy_version_name", "#_failing_TCs", "#_passing_TCs",
            "#_excluded_failing_TCs", "#_excluded_passing_TCs",
            "#_CCTs", "#_total_TCs"
        ]
        failing_tcs = []
        passing_tcs = []
        excluded_failing_tcs = []
        excluded_passing_tcs = []
        ccts = []
        total_tcs = []

        failing_tcs_set = set()
        passing_tcs_set = set()
        testsuite = set()

        too_many_failing_tcs = []
        none_failing_tcs = []
        non_passing_tcs = []

        with open(self.output_csv, "w") as f:
            f.write(",".join(csv_keys) + "\n")

            for individual in self.individual_list:
                individual_name = individual.name
                print(f"Analyzing {individual_name} on TCs statistics")

                individual = Individual(self.subject_name, self.set_name, individual_name)

                failing_tcs_set.update(individual.failing_tcs_list)
                passing_tcs_set.update(individual.passing_tcs_list)

                failing_tcs.append(len(individual.failing_tcs_list))
                passing_tcs.append(len(individual.passing_tcs_list))
                excluded_failing_tcs.append(len(individual.excluded_failing_tcs_list))
                excluded_passing_tcs.append(len(individual.excluded_passing_tcs_list))
                ccts.append(len(individual.ccts_list))
                total_tcs.append(len(individual.total_tcs_list))

                if len(individual.failing_tcs_list) > 500:
                    too_many_failing_tcs.append(individual_name)
                if len(individual.failing_tcs_list) == 0:
                    none_failing_tcs.append(individual_name)
                if len(individual.passing_tcs_list) == 0:
                    non_passing_tcs.append(individual_name)

                f.write(f"{individual_name}, {len(individual.failing_tcs_list)}, {len(individual.passing_tcs_list)}, {len(individual.excluded_failing_tcs_list)}, {len(individual.excluded_passing_tcs_list)}, {len(individual.ccts_list)}, {len(individual.total_tcs_list)}\n")

                testsuite.update(individual.total_tcs_list)
            
            with open(self.stat_dir / "total_TCs.txt", "w") as f:
                testsuite_list = list(testsuite)
                testsuite_list = sorted(testsuite_list, key=sort_testcase_script_name)
                content = "\n".join(testsuite_list)
                f.write(content)
            
            print(f"\nTotal individual: {self.set_size}")
            print(f"Total # of TCs: {len(testsuite)}")
            print(f"Average # of failing TCs: {sum(failing_tcs) / self.set_size}")
            print(f"Average # of passing TCs: {sum(passing_tcs) / self.set_size}")
            print(f"Average # of excluded failing TCs: {sum(excluded_failing_tcs) / self.set_size}")
            print(f"Average # of excluded passing TCs: {sum(excluded_passing_tcs) / self.set_size}")
            print(f"Average # of CCTs: {sum(ccts) / self.set_size}")
            print(f"Average # of total TCs: {sum(total_tcs) / self.set_size}")
            print(f"Max # of failing TCs: {max(failing_tcs)}")
            print(f"Max # of passing TCs: {max(passing_tcs)}")
            print(f"Min # of failing TCs: {min(failing_tcs)}")
            print(f"Min # of passing TCs: {min(passing_tcs)}")
            print(f"# of individuals with too many failing TCs (>500): {len(too_many_failing_tcs)}")
            print(f"# of individuals with none failing TC: {len(none_failing_tcs)}")
            print(f"# of individuals with non passing TC: {len(non_passing_tcs)}")

    def prerequisite_data(self, removed_initialization_coverage=False):
        csv_keys = [
            "buggy_version_name", "#_failing_TCs", "#_passing_TCs",
            "#_excluded_failing_TCs", "#_excluded_passing_TCs",
            "#_CCTs", "#_total_TCs",
            "#_lines_executed_by_failing_TCs", "#_lines_executed_by_passing_TCs", "#_lines_executed_by_CCTs",
            "#_total_lines_executed", "#_total_lines", "coverage", "coverage (no CCTs)",
            "#_funcs_executed_by_failing_TCs",
            "#_lines_executed_on_initialization",
            "#_funcs_executed_on_initialization",
            "#_distinct_funcs_executed_by_failing_TCs",
            "#_distinct_lines_executed_by_failing_TCs",
            "buggy_func_is_included_in_func_executed_on_initialization", # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
            "buggy_line_is_included_in_func_executed_on_initialization",
            "#_funcs", "#_files"
        ]
        failing_tcs = []
        passing_tcs = []
        excluded_failing_tcs = []
        excluded_passing_tcs = []
        ccts = []
        total_tcs = []
        lines_executed_by_failing_tcs = []
        lines_executed_by_passing_tcs = []
        lines_executed_by_CCTs = []
        total_lines_executed = []
        total_lines = []
        all_coverage = []
        all_coverage_noCCTs = []
        total_funcs_executed_by_failing_tcs = []
        total_lines_executed_on_initialization = []
        total_funcs_executed_on_initialization = []
        total_distinct_funcs_executed_by_failing_tcs = []
        total_distinct_lines_executed_by_failing_tcs = []
        total_files = []
        total_funcs = []
        total_bugfunc_included_in_initialization = 0 # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
        total_bugline_included_in_initialization = 0


        with open(self.output_csv, "w") as out_fp:
            out_fp.write(",".join(csv_keys) + "\n")

            for individual in self.individual_list:
                print(f"Analyzing {individual.name} for statistics of prerequisites")

                individual = Individual(self.subject_name, self.set_name, individual.name)
                coverage_summary_file = individual.dir_path / "coverage_summary.csv"
                assert coverage_summary_file.exists(), f"Coverage summary file {coverage_summary_file} does not exist"
                buggy_line_key = get_buggy_line_key_from_data(individual.dir_path) # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
                buggy_file = buggy_line_key.split("#")[0]
                buggy_func = buggy_line_key.split("#")[1]
                buggy_lineno = buggy_line_key.split("#")[-1]

                with open(coverage_summary_file, "r") as cov_sum_fp:
                    lines = cov_sum_fp.readlines()
                    assert len(lines) == 2, f"Coverage summary file {coverage_summary_file} is not in correct format"

                    line = lines[1].strip()
                    info = line.split(",")

                    failing_tcs.append(int(info[0]))
                    passing_tcs.append(int(info[1]))
                    excluded_failing_tcs.append(int(info[2]))
                    excluded_passing_tcs.append(int(info[3]))
                    ccts.append(int(info[4]))
                    total_tcs.append(int(info[5]))
                    lines_executed_by_failing_tcs.append(int(info[6]))
                    lines_executed_by_passing_tcs.append(int(info[7]))
                    lines_executed_by_CCTs.append(int(info[8]))
                    total_lines_executed.append(int(info[9]))
                    total_lines.append(int(info[10]))
             
                    line_key_by_fail = self.get_line_key(individual.dir_path / "coverage_info/lines_executed_by_failing_tc.json")
                    line_key_by_pass = self.get_line_key(individual.dir_path / "coverage_info/lines_executed_by_passing_tc.json")
                    line_key_by_CCT = self.get_line_key(individual.dir_path / "coverage_info/lines_executed_by_ccts.json")

                    all_key_set = set(line_key_by_fail) | set(line_key_by_pass) | set(line_key_by_CCT)
                    key_set_noCCT = set(line_key_by_fail) | set(line_key_by_pass)
                    coverage = len(all_key_set) / int(info[10])
                    all_coverage.append(coverage)
                    coverage_noCCTs = len(key_set_noCCT) / int(info[10])
                    all_coverage_noCCTs.append(coverage_noCCTs)

                    assert len(all_key_set) == int(info[9]), f"Total lines executed is not equal to the number of lines executed by failing/passing/CCTs"                    
                    info.append(coverage)
                    info.append(coverage_noCCTs)
                    info.insert(0, individual.name)

                # 2024-08-05: Measure # of functions executed by failing TCss
                lines_executed_by_failing_tcs_dict = get_lines_executed_by_failing_tcs_from_data(individual.dir_path)
                func_executed_by_failing_tcs_dict = get_file_func_pair_executed_by_failing_tcs(lines_executed_by_failing_tcs_dict)
                info.append(len(func_executed_by_failing_tcs_dict))
                # 2024-08-12: measure distinct lines by failing TCs
                lines_from_initialization = []
                if removed_initialization_coverage:
                    lines_from_initialization = get_lines_executed_on_initialization(individual.dir_path)
                info.append(len(lines_from_initialization))
                funcs_from_initialization = []
                bug_func_is_included = 0
                bug_line_is_included = 0
                for key in lines_from_initialization:
                    file_nm = key.split("#")[0]
                    func = key.split("#")[1]
                    lineno = int(key.split("#")[-1])
                    if key not in lines_from_initialization:
                        lines_from_initialization.append(key)
                    if (file_nm, func) not in funcs_from_initialization:
                        funcs_from_initialization.append((file_nm, func))
                    if buggy_file == file_nm and buggy_func == func: # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
                        bug_func_is_included = 1
                    if buggy_file == file_nm and buggy_func == func and buggy_lineno == lineno:
                        bug_line_is_included = 1
                    
                total_lines_executed_on_initialization.append(len(lines_from_initialization))
                info.append(len(funcs_from_initialization))
                total_funcs_executed_on_initialization.append(len(funcs_from_initialization))

                funcs_by_failing_tcs = []
                distinct_funcs_by_failing_tcs = []
                distinct_lines_by_failing_tcs = []
                for key in lines_executed_by_failing_tcs_dict:
                    file_nm = key.split("#")[0]
                    func = key.split("#")[1]
                    lineno = int(key.split("#")[-1])
                    if (file_nm, func) not in funcs_by_failing_tcs:
                        funcs_by_failing_tcs.append((file_nm, func))
                    
                    if (file_nm, func) not in funcs_from_initialization and (file_nm, func) not in distinct_funcs_by_failing_tcs:
                        distinct_funcs_by_failing_tcs.append((file_nm, func))
                    if key not in lines_from_initialization and key not in distinct_lines_by_failing_tcs:
                        distinct_lines_by_failing_tcs.append(key)

                info.append(len(distinct_funcs_by_failing_tcs))
                info.append(len(distinct_lines_by_failing_tcs))
                info.append(bug_func_is_included) # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
                info.append(bug_line_is_included)

                total_funcs_executed_by_failing_tcs.append(len(funcs_by_failing_tcs))
                total_distinct_funcs_executed_by_failing_tcs.append(len(distinct_funcs_by_failing_tcs))
                total_distinct_lines_executed_by_failing_tcs.append(len(distinct_lines_by_failing_tcs))
                total_bugfunc_included_in_initialization += bug_func_is_included # 2024-08-13 to check whether buggy func/line is included in func/lines executed by intialization code
                total_bugline_included_in_initialization += bug_line_is_included

                # 2024-08-05: Measure total # of files/functions of targetted files
                pp_cov_line_list = get_postprocessed_coverage_csv_file_from_data(individual.dir_path)
                funcs = []
                files = []
                for line in pp_cov_line_list[1:]:
                    key = line["key"]
                    file_nm = key.split("#")[0]
                    func = key.split("#")[1]
                    lineno = int(key.split("#")[-1])
                    if func not in funcs:
                        funcs.append(func)
                    if file_nm not in files:
                        files.append(file_nm)
                total_funcs.append(len(funcs))
                total_files.append(len(files))
                info.append(len(funcs))
                info.append(len(files))
                
                out_fp.write(",".join(map(str, info)) + "\n")

        output = ""
        output += f"\nTotal individual: {self.set_size}\n"
        output += f"Average # of failing TCs: {sum(failing_tcs) / self.set_size}\n"
        output += f"Average # of passing TCs: {sum(passing_tcs) / self.set_size}\n"
        output += f"Average # of excluded failing TCs: {sum(excluded_failing_tcs) / self.set_size}\n"
        output += f"Average # of excluded passing TCs: {sum(excluded_passing_tcs) / self.set_size}\n"
        output += f"Average # of CCTs: {sum(ccts) / self.set_size}\n"
        output += f"Average # of total TCs: {sum(total_tcs) / self.set_size}\n"
        output += f"Average # of lines executed by failing TCs: {sum(lines_executed_by_failing_tcs) / self.set_size}\n"
        output += f"Average # of lines executed by passing TCs: {sum(lines_executed_by_passing_tcs) / self.set_size}\n"
        output += f"Average # of lines executed by CCTs: {sum(lines_executed_by_CCTs) / self.set_size}\n"
        output += f"Average # of total lines executed: {sum(total_lines_executed) / self.set_size}\n"
        output += f"Average # of total lines: {sum(total_lines) / self.set_size}\n"
        output += f"Average coverage: {sum(all_coverage) / self.set_size}\n"
        output += f"Average coverage (no CCTs): {sum(all_coverage_noCCTs) / self.set_size}\n"
        output += f"Max # of failing TCs: {max(failing_tcs)}\n"
        output += f"Max # of passing TCs: {max(passing_tcs)}\n"
        output += f"Min # of failing TCs: {min(failing_tcs)}\n"
        output += f"Min # of passing TCs: {min(passing_tcs)}\n"
        output += f"Max # of lines executed by failing TCs: {max(lines_executed_by_failing_tcs)}\n"
        output += f"Min # of lines executed by failing TCs: {min(lines_executed_by_failing_tcs)}\n"
        output += f"Average # of functions executed by failing TCs: {sum(total_funcs_executed_by_failing_tcs) / self.set_size}\n"
        output += f"Average # of funcs: {sum(total_funcs) / self.set_size}\n"
        output += f"Average # of files: {sum(total_files) / self.set_size}\n"
        output += f"Average # lines executed on initialization: {sum(total_lines_executed_on_initialization) / self.set_size}\n"
        output += f"Average # funcs executed on initialization: {sum(total_funcs_executed_on_initialization) / self.set_size}\n"
        output += f"Average # distinct funcs executed by failing TCs: {sum(total_distinct_funcs_executed_by_failing_tcs) / self.set_size}\n"
        output += f"Average # distinct lines executed by failing TCs: {sum(total_distinct_lines_executed_by_failing_tcs) / self.set_size}\n"
        output += f"# of versions where buggy func is included in func executed on initialization: {total_bugfunc_included_in_initialization}\n"
        output += f"# of versions where buggy line is included in func executed on initialization: {total_bugline_included_in_initialization}\n"

        print(output)
        stat_summary_filename = self.output_csv.name.split(".")[0] + "-stats-summary.txt"
        with open(self.stat_dir / stat_summary_filename, "w") as f:
            f.write(output)

    def get_line_key(self, file_path):
        assert file_path.exists(), f"{file_path} does not exist"
        with open(file_path, "r") as fp:
            data = json.load(fp)
            key_list = list(data.keys())
        return key_list

    def crashed_buggy_mutants(self,):
        stat_dict = {}
        self.individual_list = get_files_in_dir(self.set_dir)

        for individual_file in self.individual_list:
            filename = individual_file.name
            info = filename.split("-")
            version_name = info[0]
            target_file = version_name.split(".")[0] + "." + version_name.split(".")[2]
            crash_type = info[1]
            stage = info[2]

            if target_file not in stat_dict:
                stat_dict[target_file] = {}
            
            if stage not in stat_dict[target_file]:
                stat_dict[target_file][stage] = {}
            
            if crash_type not in stat_dict[target_file][stage]:
                stat_dict[target_file][stage][crash_type] = 0
            stat_dict[target_file][stage][crash_type] += 1

            
            # with open(individual_file, "r") as fp:
            #     lines = fp.readlines()
            #     line_info = lines[0].strip().split(",")
            #     line_name = line_info[0]
            #     line_crash_type = line_info[1]
            #     line_exit_num = line_info[2]

            #     crash_id = f"{line_crash_type}:{line_exit_num}"
            #     if crash_id not in stat_dict[target_file]:
            #         stat_dict[target_file][crash_id] = 0
            #     stat_dict[target_file][crash_id] += 1
        
        txt_name = self.output_csv.name.split(".")[0] + ".json"
        self.output_json = self.stat_dir / txt_name

        with open(self.output_json, "w") as fp:
            print(json.dumps(stat_dict, indent=2))
            json.dump(stat_dict, fp, ensure_ascii=False, indent=2)
            # for target in stat_dict:
            #     fp.write(f"file: {target}\n")
            #     print(f"file: {target}")
            #     for crash_id in stat_dict[target]:
            #         fp.write(f"\tcrash id: {crash_id}, count: {stat_dict[target][crash_id]}\n")
            #         print(f"\tcrash id: {crash_id}, count: {stat_dict[target][crash_id]}")
                
