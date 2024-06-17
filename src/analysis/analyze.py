from copy import deepcopy
import random
import subprocess as sp

from lib.utils import *
from analysis.individual import Individual
        

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
        
        print(f"\n\nTotal # of buggy versions: {len(self.individual_list)}")
        print(f"Total # of reduced tcs: {len(reduced_test_suite)}")
        print(f"# of excluded failing tcs: {len(failing_tcs_list)}")
        print(f"# of excluded passing tcs: {len(passing_tcs_list)}")
        print(f"Total # of excluded tcs: {len(excluded_tc_list)}")

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
            if len(reduced_failing_tcs_list) == 0 and len(reduced_passing_tcs_list) == 0:
                excluded_individual_cnt += 1
                continue

            included_individual_cnt += 1
            sp.check_call(["cp", "-r", individual.individual_dir, reduced_individuals_dir])

            reduced_individual_dir = reduced_individuals_dir / individual_name
            assert reduced_individual_dir.exists(), f"Reduced individual directory {reduced_individual_dir} does not exist"

            new_testsuite_dir = reduced_individual_dir / "testsuite_info"
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
        print(f"Total individual: {len(self.individual_list)}")
        print(f"Total included individual: {included_individual_cnt}")
        print(f"Total excluded individual: {excluded_individual_cnt}")

    def appropriate_version_with_all_failing_tcs(self):

        appropiate_individuals_dir = out_dir / self.subject_name / f"{self.set_name}-appropriate"
        appropiate_individuals_dir.mkdir(exist_ok=True, parents=True)

        included_buggy_version_cnt = 0
        excluded_buggy_version_cnt = 0
        for individual in self.individual_list:
            individual_name = individual.name
            print(f"Analyzing {individual_name} for appropriate versions with all failing TCs")

            individual = Individual(self.subject_name, self.set_name, individual_name)

            failing_tcs_set = set(individual.failing_tcs_list)
            excluded_failing_tc_set = set(individual.excluded_failing_tcs_list)

            total_failing_tcs_set = failing_tcs_set.union(excluded_failing_tc_set)

            if len(total_failing_tcs_set) < 500:
                sp.run(["cp", "-r", individual.individual_dir, appropiate_individuals_dir])
                included_buggy_version_cnt += 1
            else:
                excluded_buggy_version_cnt += 1
        
        print(f"Number of buggy versions included: {included_buggy_version_cnt}")
        print(f"Number of buggy versions excluded: {excluded_buggy_version_cnt}")

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

        with open(self.output_csv, "w") as f:
            f.write(",".join(csv_keys) + "\n")

            for individual in self.individual_list:
                print(f"Analyzing {individual.name} for statistics of prerequisites")

                individual = Individual(self.subject_name, self.set_name, individual.name)
                coverage_summary_file = individual.individual_dir / "coverage_summary.csv"
                assert coverage_summary_file.exists(), f"Coverage summary file {coverage_summary_file} does not exist"

                with open(coverage_summary_file, "r") as f:
                    lines = f.readlines()
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
                    f.write(",".join(map(str, info)) + "\n")

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
        