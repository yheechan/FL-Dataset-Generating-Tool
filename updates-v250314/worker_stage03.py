import subprocess as sp
import json
import os
import random

from lib.utils import *
from lib.worker_base import Worker

class WorkerStage03(Worker):
    def __init__(
            self, subject_name, machine, core, version_name,
            need_configure, last_version,
            use_excluded_failing_tcs,
            passing_tcs_perc=1.0, failing_tcs_perc=1.0, verbose=False
    ):
        super().__init__(subject_name, "stage03", "prepare_prerequisites", machine, core, verbose)
        
        self.assigned_works_dir = self.core_dir / f"stage03-assigned_works"
        self.need_configure = need_configure
        self.last_version = last_version

        self.passing_tcs_perc = passing_tcs_perc
        self.failing_tcs_perc = failing_tcs_perc
        self.use_excluded_failing_tcs = use_excluded_failing_tcs

        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.target_code_file, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_dir)
        self.target_code_file_path = self.core_dir / self.target_code_file
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.version_dir)

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)

        self.extract_exe = self.tools_dir / "extractor"

        self.core_repo_dir = self.core_dir / self.name

        self.set_filtered_files_for_gcovr()
        self.set_target_preprocessed_files()

        self.prerequisite_data_dir = out_dir / f"{self.name}" / "prerequisite_data"
        self.prerequisite_data_dir.mkdir(exist_ok=True, parents=True)

        self.allPassisCCTdir = out_dir / f"{self.name}" / "allPassisCCT"
        self.allPassisCCTdir.mkdir(exist_ok=True, parents=True)

        self.cov_dir = self.core_dir / "coverage" / self.version_dir.name
        if self.cov_dir.exists():
            print_command(["rm", "-rf", self.cov_dir], self.verbose)
            sp.check_call(["rm", "-rf", self.cov_dir])
        print_command(["mkdir", "-p", self.cov_dir], self.verbose)
        self.cov_dir.mkdir(exist_ok=True, parents=True)

    def run(self):
        print(f"Testing version {self.version_dir.name} on {self.machine}::{self.core}")

        # 1. Configure subject
        if self.need_configure:
            self.configure_yes_cov()
        
        # 2. Build subject
        self.build()
        self.set_env()

        # 4. Test version
        self.test_version()
        if self.last_version:
            self.clean_build()
    
    def test_version(self):

        # 1. Extract line2function mapping 
        res = self.extract_line2function()
        self.set_line2function_dict(self.version_dir)
        if res != 0:
            print(f"Failed to extract line2function on {self.version_dir.name}")
            return

        # 2. Measure coverage
        res = self.measure_coverage()
        if res == 2:
            print(f"All passing TCs in {self.version_dir.name} is a CCT...!")
            return
        elif res != 0:
            print(f"Failed to measure coverage on {self.version_dir.name}")
            return

        # 3. Postprocess coverage
        self.postprocess_coverage()

        # 4. Save the version to self.prerequisite_data_dir
        self.save_version(self.version_dir, self.prerequisite_data_dir)
    
    def postprocess_coverage(self):
        self.total_tcs = self.failing_tcs_list + self.passing_tcs_list + self.excluded_failing_tcs_list + self.excluded_passing_tcs_list + self.ccts_list
        self.coverage_summary = {
            "#_failing_TCs": len(self.failing_tcs_list),
            "#_passing_TCs": len(self.passing_tcs_list),
            "#_excluded_failing_TCs": len(self.excluded_failing_tcs_list),
            "#_excluded_passing_TCs": len(self.excluded_passing_tcs_list),
            "#_CCTs": len(self.ccts_list),
            "#_total_TCs": len(self.total_tcs),
            "#_lines_executed_by_failing_tcs": 0,
            "#_lines_executed_by_passing_tcs": 0,
            '#_lines_executed_by_ccts': 0,
            "#_total_lines_executed": 0,
            "#_total_lines": 0,
        }

        self.set_line2function_dict(self.version_dir)
        self.buggy_line_key = self.make_key(self.target_code_file, self.buggy_lineno)
        print_command([">> buggy_line_key: ", self.buggy_line_key], self.verbose)

        self.version_coverage_dir = self.version_dir / "coverage_info"
        print_command(["mkdir", "-p", self.version_coverage_dir], self.verbose)
        self.version_coverage_dir.mkdir(exist_ok=True)

        total_tc_list = self.failing_tcs_list + self.passing_tcs_list + self.ccts_list
        total_tc_list = sorted(total_tc_list, key=sort_testcase_script_name)
        print_command([">> total_tc_list length: ", len(total_tc_list)], self.verbose)

        # make a csv file for coverage where the column is each test case
        # and the row is each line key (filename#function_name#line_number)
        # the contents is 0 or 1 (0: not covered, 1: covered)
        first = True
        cov_data = {
            "col_data": [],
            "row_data": []
        }
        cov_data_noCCTs = {
            "col_data": [],
            "row_data": []
        }
        self.lines_execed_by_failing_tc = {}
        self.lines_execed_by_passing_tc = {}
        self.lines_execed_by_ccts = {}
        self.lines_execed = {}
        # postprocess coverage for all test cases (failing, passing, ccts) at postprocessed_coverage.csv
        # postprocess coverage for all test cases (failing, passing) at postprocessed_coverage_noCCTs.csv
        for idx, tc_script_name in enumerate(total_tc_list):
            # print(f"Processing {idx+1}/{len(total_tc_list)}: {tc_script_name}")

            tc_name = tc_script_name.split(".")[0]
            tc_cov_filename = f"{tc_name}.raw.json"
            tc_cov_file = self.cov_dir / tc_cov_filename
            assert tc_cov_file.exists(), f"Test case coverage file {tc_cov_file} does not exist"

            tc_cov_json = json.load(tc_cov_file.open())

            if first:
                first = False
                self.add_key_data(cov_data, tc_cov_json)
                self.add_key_data(cov_data_noCCTs, tc_cov_json, False)

            self.add_cov_data(
                cov_data, cov_data_noCCTs, tc_cov_json, tc_script_name,
            )
        
        self.coverage_summary["#_lines_executed_by_failing_tcs"] = len(self.lines_execed_by_failing_tc)
        self.coverage_summary["#_lines_executed_by_passing_tcs"] = len(self.lines_execed_by_passing_tc)
        self.coverage_summary["#_lines_executed_by_ccts"] = len(self.lines_execed_by_ccts)
        self.coverage_summary["#_total_lines_executed"] = len(self.lines_execed)
        
        # write coverage data to a csv file
        self.write_postprocessed_coverage(cov_data, "postprocessed_coverage.csv")
        self.write_postprocessed_coverage(cov_data_noCCTs, "postprocessed_coverage_noCCTs.csv")
        self.write_executed_lines(self.lines_execed_by_failing_tc, "lines_executed_by_failing_tc.json")
        self.write_executed_lines(self.lines_execed_by_passing_tc, "lines_executed_by_passing_tc.json")
        self.write_executed_lines(self.lines_execed_by_ccts, "lines_executed_by_ccts.json")
        self.write_summary()
        self.write_buggy_line_key()
    
    def write_buggy_line_key(self):
        buggy_line_key_file = self.version_dir / "buggy_line_key.txt"
        with open(buggy_line_key_file, "w") as f:
            f.write(self.buggy_line_key)
        
        print(f"Buggy line key is saved at {buggy_line_key_file.name}")

    def write_summary(self):
        cov_summary_file = self.version_dir / "coverage_summary.csv"
        columns = self.coverage_summary.keys()
        with open(cov_summary_file, "w") as f:
            f.write(",".join(columns) + "\n")
            f.write(",".join([str(self.coverage_summary[key]) for key in columns]) + "\n")
        
        print(f"Coverage summary is saved at {cov_summary_file.name}")

    def write_executed_lines(self, lines_execed_by_tc, filename):
        lines_execed_by_tc_file = self.version_coverage_dir / filename
        with open(lines_execed_by_tc_file, "w") as f:
            json.dump(lines_execed_by_tc, f)
        
        print(f"Executed lines by test cases are saved at {lines_execed_by_tc_file.name}")
    
    def write_initialization_lines(self, lines_execed_at_initialization, filename):
        self.version_coverage_dir = self.version_dir / "coverage_info"
        print_command(["mkdir", "-p", self.version_coverage_dir], self.verbose)
        self.version_coverage_dir.mkdir(exist_ok=True)

        lines_execed_on_init_file = self.version_coverage_dir / filename
        with open(lines_execed_on_init_file, "w") as f:
            content = "\n".join(lines_execed_at_initialization)
            f.write(content)
        print(f"Lines executed on initialization saved at {lines_execed_on_init_file.name}")

    def write_postprocessed_coverage(self, cov_data, cov_csv_filename):
        cov_csv_file = self.version_coverage_dir / cov_csv_filename
        with open(cov_csv_file, "w") as f:
            f.write(",".join(cov_data["col_data"]) + "\n")

            for row in cov_data["row_data"]:
                f.write(",".join([f"\"{str(x)}\"" for x in row]) + "\n")
        
        print(f"Coverage csv file is saved at {cov_csv_file.name}")
    
    def add_cov_data(self, cov_data, cov_data_noCCTs, tc_cov_json, tc_script_name):
        tc_name = tc_script_name.split(".")[0]

        pass_or_fail = False if tc_script_name in self.failing_tcs_list else True
        isCCTs = False
        if pass_or_fail:
            if tc_script_name in self.passing_tcs_list:
                assert tc_script_name in self.passing_tcs_list, f"Test case {tc_script_name} is not in passing test cases"
            else:
                assert tc_script_name in self.ccts_list, f"Test case {tc_script_name} is not in CCTs"                
                isCCTs = True
        
        cov_data["col_data"].append(tc_name)
        if isCCTs == False:
            cov_data_noCCTs["col_data"].append(tc_name)
        
        cnt = 0
        for file in tc_cov_json["files"]:
            filename = file["file"]
            for i in range(len(file["lines"])):
                line = file["lines"][i]
                lineno = line["line_number"]
                key = self.make_key(filename, lineno)
                curr_row_key = cov_data["row_data"][cnt][0]
                assert key == curr_row_key, f"Key {key} does not match with the row data key {curr_row_key}"

                covered = 1 if line["count"] > 0 else 0
                cov_data["row_data"][cnt].append(covered)

                if isCCTs == False:
                    cov_data_noCCTs["row_data"][cnt].append(covered)

                if covered == 1:
                    if key not in self.lines_execed:
                        self.lines_execed[key] = 0
                    self.lines_execed[key] += 1

                    if pass_or_fail and isCCTs == False:
                        if key not in self.lines_execed_by_passing_tc:
                            self.lines_execed_by_passing_tc[key] = []
                        self.lines_execed_by_passing_tc[key].append(tc_script_name)
                    elif pass_or_fail and isCCTs == True:
                        if key not in self.lines_execed_by_ccts:
                            self.lines_execed_by_ccts[key] = []
                        self.lines_execed_by_ccts[key].append(tc_script_name)
                    else:
                        if key not in self.lines_execed_by_failing_tc:
                            self.lines_execed_by_failing_tc[key] = []
                        self.lines_execed_by_failing_tc[key].append(tc_script_name)

                # assert that failing line executes buggy line
                if not pass_or_fail and key == self.buggy_line_key and int(self.buggy_lineno) != -1:
                    assert covered == 1, f"Failing test case {tc_script_name} does not execute buggy line {self.buggy_line_key}"
                    print(f"Failing test case {tc_script_name} executes buggy line {self.buggy_line_key}")
                
                cnt += 1

    def add_key_data(self, cov_data, tc_cov_json, is_all=True):
        cov_data["col_data"].append("key")

        for file in tc_cov_json["files"]:
            filename = file["file"]
            for line in file["lines"]:
                lineno = line["line_number"]
                key = self.make_key(filename, lineno)
                
                assert [key] not in cov_data["row_data"], f"Key {key} already exists in the row data"
                cov_data["row_data"].append([key])
                if is_all:
                    self.coverage_summary["#_total_lines"] += 1

    
    def measure_coverage(self):
        
        # 1. Make patch file
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")

        # 2. Apply patch
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Build the subject, if build fails, skip the version
        res = self.build()
        if res != 0:
            print(f"Failed to build on {self.version_dir.name}")
            self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
            return 1
        
        # 4. Run test cases
        self.ccts_list = []
        if self.use_excluded_failing_tcs:
            self.move_excluded_failing_tcs()
        if self.passing_tcs_perc < 1.0:
            self.passing_tcs_list, self.excluded_passing_tcs_list = self.move_tcs(
                self.passing_tcs_list, self.excluded_passing_tcs_list,
                "passing_tcs.txt", "excluded_passing_tcs.txt", self.passing_tcs_perc
            )
        if self.failing_tcs_perc < 1.0:
            self.failing_tcs_list, self.excluded_failing_tcs_list = self.move_tcs(
                self.failing_tcs_list, self.excluded_failing_tcs_list,
                "failing_tcs.txt", "excluded_failing_tcs.txt", self.failing_tcs_perc
            )
        
        for tc_script_name in self.failing_tcs_list+self.passing_tcs_list:
            # 4-1. remove past coverage
            self.remove_all_gcda(self.core_repo_dir)

            # 4-2. Run test case
            res = self.run_test_case(tc_script_name)
            
            # 4-3. Remove untarged files for coverage
            self.remove_untargeted_files_for_gcovr(self.core_repo_dir)

            # 4-4. Collect coverage
            raw_cov_file = self.generate_coverage_json(
                self.core_repo_dir, self.cov_dir, tc_script_name,
            )

            # 4-5. Check if the buggy line is coveraged
            if tc_script_name in self.failing_tcs_list:
                buggy_line_covered = self.check_buggy_line_covered(
                    tc_script_name, raw_cov_file, self.target_code_file, self.buggy_lineno
                )
                if buggy_line_covered == 1:
                    print(f">> Buggy line {self.buggy_lineno} is NOT covered by failing TC {tc_script_name}")
                elif buggy_line_covered == -2:
                    print(f">> Failed to check coverage for failing TC {tc_script_name}")
                else:
                    print(f">> Buggy line {self.buggy_lineno} is covered by failing TC {tc_script_name}")
            elif tc_script_name in self.passing_tcs_list and int(self.buggy_lineno) != -1:
                # check_buggy_line_covered return 0 if the buggy line is covered
                # and 1 if the buggy line is not covered
                buggy_line_covered = self.check_buggy_line_covered(
                    tc_script_name, raw_cov_file, self.target_code_file, self.buggy_lineno
                )
                if buggy_line_covered == 0:
                    self.ccts_list.append(tc_script_name)
                    # os.remove(raw_cov_file) # 2024-09-17 Do not remove raw cov of ccts
        
        # 2024-08-12 SAVE INITIALIZATION CODE COVERAGE
        self.save_initialization_code_coverage()
        
        # 5. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)

        # 6. Write ccts.txt file
        self.update_ccts()

        if len(self.passing_tcs_list) == 0:
            log_file = self.allPassisCCTdir / f"{self.version_dir.name}"
            with open(log_file, "w") as fp:
                log = f"{self.version_dir.name},allPassisCCT"
                fp.write(log)
            return 2

        return 0
    
    def save_initialization_code_coverage(self): # 2024-08-12 SAVE INITIALIZATION CODE COVERAGE
        # 4-1. remove past coverage
        self.remove_all_gcda(self.core_repo_dir)

        # 4-2. Run test case
        if self.config["test_initialization"]["status"] == True:
            exec_wd = self.core_dir / self.config["test_initialization"]["execution_path"]
            res = sp.run(
                self.config["test_initialization"]["init_cmd"],
                shell=True, cwd=exec_wd, # 2024-08-12 SPECIFICALLY CHANGE THIS MANUALLY
                stderr=sp.PIPE, stdout=sp.PIPE,
                env=self.my_env
            )
        
        # 4-3. Remove untarged files for coverage
        self.remove_untargeted_files_for_gcovr(self.core_repo_dir)

        # 4-4. Collect coverage
        tc_script_name = "initialization"
        raw_cov_file = self.generate_coverage_json(
            self.core_repo_dir, self.cov_dir, tc_script_name,
        )

        # 4-5. Check if the buggy line is coveraged
        buggy_line_covered = self.check_buggy_line_covered(
            tc_script_name, raw_cov_file, self.target_code_file, self.buggy_lineno
        )
        if buggy_line_covered == 1:
            print(f">> Buggy line {self.buggy_lineno} is NOT covered by failing TC {tc_script_name}")
        if buggy_line_covered == -2:
            print(f">> Failed to check coverage for failing TC {tc_script_name}")
        if buggy_line_covered == 0:
            print(f">> Buggy line {self.buggy_lineno} is covered by failing TC {tc_script_name}")

        # make list of lines 2 keys
        lines2keys_intialization = []
        tc_cov_json = json.load(raw_cov_file.open())
        for file in tc_cov_json["files"]:
            filename = file["file"]
            for i in range(len(file["lines"])):
                line = file["lines"][i]
                lineno = line["line_number"]
                key = self.make_key(filename, lineno)

                covered = 1 if line["count"] > 0 else 0

                if covered == 1:
                    lines2keys_intialization.append(key)
        
        self.write_initialization_lines(lines2keys_intialization, "lines_executed_at_initialization.txt")

    
    def update_ccts(self):
        if len(self.ccts_list) > 0:
            self.passing_tcs_list = list(set(self.passing_tcs_list) - set(self.ccts_list))
            self.passing_tcs_list = sorted(self.passing_tcs_list, key=sort_testcase_script_name)

            with open(self.version_dir / "testsuite_info" / "passing_tcs.txt", "w") as f:
                content = "\n".join(self.passing_tcs_list)
                f.write(content)
        
        self.ccts_list = sorted(self.ccts_list, key=sort_testcase_script_name)
        with open(self.version_dir / "testsuite_info" / "ccts.txt", "w") as f:
            content = "\n".join(self.ccts_list)
            f.write(content)
        
        self.passing_tcs_list = get_tc_list(self.version_dir / "testsuite_info" / "passing_tcs.txt")
        self.ccts_list = get_tc_list(self.version_dir / "testsuite_info" / "ccts.txt")
    
    def move_tcs(self, tc_list, excluded_tc_list, tc_file_name, excluded_tc_file_name, perc):
        tc_set = set(tc_list)
        excluded_tc_set = set(excluded_tc_list)

        tcs_len = len(tc_list)
        tcs_len_to_use = int(tcs_len * perc)
        tcs_len_to_exclude = tcs_len - tcs_len_to_use

        if tcs_len < 10:
            print(f"Too few test cases {tcs_len} to exclude")
            return tc_list, excluded_tc_list
        
        # if the tcs_len_to_use is less than 10, but the tcs_len is more than 10
        # then use 10 test cases from tcs_list
        if tcs_len_to_use < 10:
            tcs_len_to_use = 10
            tcs_len_to_exclude = tcs_len - tcs_len_to_use
        
        if tcs_len_to_exclude > 0:
            # randomly select test cases to exclude
            excluded_tcs = random.sample(tc_list, tcs_len_to_exclude)
            excluded_tc_set = excluded_tc_set.union(set(excluded_tcs))
            tc_set = tc_set - set(excluded_tcs)

            with open(self.version_dir / "testsuite_info" / tc_file_name, "w") as f:
                tc_list = list(tc_set)
                tc_list = sorted(tc_list, key=sort_testcase_script_name)
                content = "\n".join(tc_list)
                f.write(content)

            with open(self.version_dir / "testsuite_info" / excluded_tc_file_name, "w") as f:
                excluded_tc_list = list(excluded_tc_set)
                excluded_tc_list = sorted(excluded_tc_list, key=sort_testcase_script_name)
                content = "\n".join(excluded_tc_list)
                f.write(content)
        
        tc_list = get_tc_list(self.version_dir / "testsuite_info" / tc_file_name)
        excluded_tc_list = get_tc_list(self.version_dir / "testsuite_info" / excluded_tc_file_name)
        
        return tc_list, excluded_tc_list
    
    def move_excluded_failing_tcs(self):
        failing_tcs_set = set(self.failing_tcs_list)
        excluded_failing_tcs_set = set(self.excluded_failing_tcs_list)

        all_failing_tcs_set = failing_tcs_set.union(excluded_failing_tcs_set)
        all_failing_tcs_list = list(all_failing_tcs_set)
        all_failing_tcs_list = sorted(all_failing_tcs_list, key=sort_testcase_script_name)

        with open(self.version_dir / "testsuite_info" / "failing_tcs.txt", "w") as f:
            content = "\n".join(all_failing_tcs_list)
            f.write(content)

        with open(self.version_dir / "testsuite_info" / "excluded_failing_tcs.txt", "w") as f:
            f.write("")
        
        self.failing_tcs_list = get_tc_list(self.version_dir / "testsuite_info" / "failing_tcs.txt")
        self.excluded_failing_tcs_list = get_tc_list(self.version_dir / "testsuite_info" / "excluded_failing_tcs.txt")
    
    def extract_line2function(self):
        # 1. Make patch file
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")

        # 2. Apply patch
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Build the subject, if build fails, skip the version
        res = self.build()
        if res != 0:
            print(f"Failed to build on {self.version_dir.name}")
            self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
            return 1
        
        # 4. Extract line2function mapping
        perfile_line2function_data = {}
        for pp_file_str in self.target_preprocessed_files:
            pp_file = self.core_dir / pp_file_str
            assert pp_file.exists(), f"Preprocessed file {pp_file} does not exist"

            cmd = [self.extract_exe, pp_file.__str__()]
            process= sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, encoding="utf-8")

            while True:
                line = process.stdout.readline()
                if line == "" and process.poll() != None:
                    break
                line = line.strip()
                if line == "":
                    continue
                    
                # ex) one##htmlReadDoc(const xmlChar * cur, const char * URL, const char * encoding, int options)##6590##6603##HTMLparser.c:6590:1##HTMLparser.c
                data = line.split("##")
                class_name = data[0]
                function_name = data[1]
                start_line = data[2]
                end_line = data[3]
                originated_file = data[4]
                file_data = originated_file.split(":")[0]
                filename = data[5]

                if file_data not in perfile_line2function_data:
                    perfile_line2function_data[file_data] = []
            
                full_function_name = f"{class_name}::{function_name}" if class_name != "None" else function_name
                data = (full_function_name, start_line, end_line)
                if data not in perfile_line2function_data[file_data]:
                    perfile_line2function_data[file_data].append(data)
            
            print(f">> Extracted line2function data from {pp_file.name}")
        
        # 5. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)

        # 6. Save the buggy version
        line2function_file = self.save_line2function(self.version_dir, perfile_line2function_data)
        print(f">> Extracted line2function data saved to {line2function_file.name}")

        return 0
    
    def save_line2function(self, version_dir, perfile_line2function_data):
        line2function_dir = self.version_dir / "line2function_info"
        print_command(["mkdir", "-p", line2function_dir], self.verbose)
        line2function_dir.mkdir(exist_ok=True)

        line2function_file = line2function_dir / "line2function.json"
        with open(line2function_file, "w") as f:
            json.dump(perfile_line2function_data, f, ensure_ascii=False, indent=2)
        
        return line2function_file