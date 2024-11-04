from copy import deepcopy
import random
import subprocess as sp
import csv
import json

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
                
