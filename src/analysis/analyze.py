from copy import deepcopy
import random
import subprocess as sp
import csv

from lib.utils import *
from analysis.individual import Individual
from lib.experiment import Experiment
from analysis.rank_utils import *
        

class Analyze:
    def __init__(
            self, subject_name, set_name, output_csv,
        ):
        self.subject_name = subject_name
        
        self.set_name = set_name
        self.set_dir = out_dir / self.subject_name / self.set_name
        self.individual_list = get_dirs_in_dir(self.set_dir)
        self.set_size = len(self.individual_list)

        self.stat_dir = stats_dir / self.subject_name
        self.stat_dir.mkdir(exist_ok=True, parents=True)

        if not output_csv.endswith(".csv"):
            output_csv += ".csv"
        self.output_csv = self.stat_dir / output_csv
    
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

    def prerequisite_data(self):
        csv_keys = [
            "buggy_version_name", "#_failing_TCs", "#_passing_TCs",
            "#_excluded_failing_TCs", "#_excluded_passing_TCs",
            "#_CCTs", "#_total_TCs",
            "#_lines_executed_by_failing_TCs", "#_lines_executed_by_passing_TCs",
            "#_total_lines_executed", "#_total_lines", "coverage"
        ]
        failing_tcs = []
        passing_tcs = []
        excluded_failing_tcs = []
        excluded_passing_tcs = []
        ccts = []
        total_tcs = []
        lines_executed_by_failing_tcs = []
        lines_executed_by_passing_tcs = []
        total_lines_executed = []
        total_lines = []
        all_coverage = []

        with open(self.output_csv, "w") as out_fp:
            out_fp.write(",".join(csv_keys) + "\n")

            for individual in self.individual_list:
                print(f"Analyzing {individual.name} for statistics of prerequisites")

                individual = Individual(self.subject_name, self.set_name, individual.name)
                coverage_summary_file = individual.dir_path / "coverage_summary.csv"
                assert coverage_summary_file.exists(), f"Coverage summary file {coverage_summary_file} does not exist"

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
                    total_lines_executed.append(int(info[8]))
                    total_lines.append(int(info[9]))

                    coverage = int(info[8]) / int(info[9])
                    all_coverage.append(coverage)

                    info.append(coverage)
                    info.insert(0, individual.name)
                    out_fp.write(",".join(map(str, info)) + "\n")

        print(f"\nTotal individual: {self.set_size}")
        print(f"Average # of failing TCs: {sum(failing_tcs) / self.set_size}")
        print(f"Average # of passing TCs: {sum(passing_tcs) / self.set_size}")
        print(f"Average # of excluded failing TCs: {sum(excluded_failing_tcs) / self.set_size}")
        print(f"Average # of excluded passing TCs: {sum(excluded_passing_tcs) / self.set_size}")
        print(f"Average # of CCTs: {sum(ccts) / self.set_size}")
        print(f"Average # of total TCs: {sum(total_tcs) / self.set_size}")
        print(f"Average # of lines executed by failing TCs: {sum(lines_executed_by_failing_tcs) / self.set_size}")
        print(f"Average # of lines executed by passing TCs: {sum(lines_executed_by_passing_tcs) / self.set_size}")
        print(f"Average # of total lines executed: {sum(total_lines_executed) / self.set_size}")
        print(f"Average # of total lines: {sum(total_lines) / self.set_size}")
        print(f"Average coverage: {sum(all_coverage) / self.set_size}")
        print(f"Max # of failing TCs: {max(failing_tcs)}")
        print(f"Max # of passing TCs: {max(passing_tcs)}")
        print(f"Min # of failing TCs: {min(failing_tcs)}")
        print(f"Min # of passing TCs: {min(passing_tcs)}")
