import subprocess as sp
import json
import os
import random

from lib.utils import *
from lib.worker_base import Worker

class WorkerStage03(Worker):
    def __init__(
            self, subject_name, experiment_name,
            machine, core, version_name,
            need_configure, last_version,
            verbose=False
    ):
        super().__init__(subject_name, "stage03", "prepare_prerequisites", machine, core, verbose)

        self.experiment_name = experiment_name
        
        self.assigned_works_dir = self.core_dir / f"stage03-assigned_works"
        self.need_configure = need_configure
        self.last_version = last_version

        self.version_name = version_name
        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.connect_to_db()
        self.target_code_file, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_name, self.experiment_name)
        self.target_code_file_path = self.core_dir / self.target_code_file
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.version_name, self.experiment_name)

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
        self.save_version(self.version_dir, "prerequisites", self.experiment_name)
        print_command(["cp", "-r", self.version_dir, self.prerequisite_data_dir], self.verbose)
        sp.check_call(["cp", "-r", self.version_dir, self.prerequisite_data_dir])

        # 5. delete the coverage directory
        sp.check_call(["rm", "-rf", self.cov_dir])
    
    def postprocess_coverage(self):
        self.set_testcases(self.version_name, self.experiment_name)
        self.total_tcs = self.failing_tcs_list + self.passing_tcs_list + self.excluded_failing_tcs_list + self.excluded_passing_tcs_list + self.ccts_list
        self.coverage_summary = {
            "num_failing_tcs": len(self.failing_tcs_list),
            "num_passing_tcs": len(self.passing_tcs_list),
            "num_ccts": len(self.ccts_list),
            "num_total_tcs": len(self.total_tcs),
            "num_lines_executed_by_failing_tcs": 0,
            "num_lines_executed_by_passing_tcs": 0,
            'num_lines_executed_by_ccts': 0,
            "num_total_lines_executed": 0,
            "num_total_lines": 0,
        }

        # Make buggy line key and write to bug_info table
        self.buggy_line_key = self.make_key(self.target_code_file, self.buggy_lineno)
        print_command([">> buggy_line_key: ", self.buggy_line_key], self.verbose)

        if not self.db.column_exists("bug_info", "buggy_line_key"):
            self.db.add_column("bug_info", "buggy_line_key TEXT DEFAULT NULL")
        self.db.update(
            "bug_info",
            set_values={"buggy_line_key": self.buggy_line_key},
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
                "version": self.version_name
            }
        )

        # Make coverage csv file
        if not self.db.column_exists("tc_info", "cov_bit_seq"):
            self.db.add_column("tc_info", "cov_bit_seq TEXT DEFAULT NULL")


        total_tc_list = self.failing_tcs_list + self.passing_tcs_list + self.ccts_list
        total_tc_list = sorted(total_tc_list, key=sort_testcase_script_name)
        print_command([">> total_tc_list length: ", len(total_tc_list)], self.verbose)

        # make a csv file for coverage where the column is each test case
        # and the row is each line key (filename#function_name#line_number)
        # the contents is 0 or 1 (0: not covered, 1: covered)
        first = True
        cov_data = {
            "col_data": [],
            "row_data": {} 
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

            self.add_cov_data(
                cov_data, tc_cov_json, tc_script_name, first=first
            )
            first = False
        
        self.coverage_summary["num_lines_executed_by_failing_tcs"] = len(self.lines_execed_by_failing_tc)
        self.coverage_summary["num_lines_executed_by_passing_tcs"] = len(self.lines_execed_by_passing_tc)
        self.coverage_summary["num_lines_executed_by_ccts"] = len(self.lines_execed_by_ccts)
        self.coverage_summary["num_total_lines_executed"] = len(self.lines_execed)
        
        # write coverage data to a csv file
        self.write_postprocessed_coverage(cov_data)
        self.write_lines(cov_data["col_data"])
        self.write_executed_lines(self.lines_execed_by_failing_tc, "lines_executed_by_failing_tc.json")
        self.write_executed_lines(self.lines_execed_by_passing_tc, "lines_executed_by_passing_tc.json")
        self.write_executed_lines(self.lines_execed_by_ccts, "lines_executed_by_ccts.json")
        self.write_summary()
        self.write_buggy_line_key()
    
    def write_buggy_line_key(self):
        if not self.db.column_exists("bug_info", "buggy_line_key"):
            self.db.add_column("bug_info", "buggy_line_key TEXT DEFAULT NULL")
        self.db.update(
            "bug_info",
            set_values={"buggy_line_key": self.buggy_line_key},
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
                "version": self.version_name
            }
        )


    def write_summary(self):
        for col in self.coverage_summary:
            if not self.db.column_exists("bug_info", col):
                self.db.add_column("bug_info", f"{col} INT DEFAULT NULL")
        
        self.db.update(
            "bug_info",
            set_values=self.coverage_summary,
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
                "version": self.version_name
            }
        )


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

    def write_postprocessed_coverage(self, cov_data):
        for tc_script_name in cov_data["row_data"]:
            cov_bit_seq = cov_data["row_data"][tc_script_name]
            self.db.update(
                "tc_info",
                set_values={"cov_bit_seq": cov_bit_seq},
                conditions={
                    "subject": self.name,
                    "experiment_name": self.experiment_name,
                    "version": self.version_name,
                    "tc_name": tc_script_name
                }
            )
    
    def write_lines(self, col_data):
        if not self.db.table_exists("line_info"):
            self.db.create_table(
                "line_info",
                "subject TEXT, experiment_name TEXT, version TEXT, line_key TEXT, line_id INT, is_buggy_line BOOLEAN DEFAULT NULL"
            )
        
        self.db.delete(
            "line_info",
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
                "version": self.version_name
            }
        )
        
        for idx, key in enumerate(col_data):
            cols = "subject, experiment_name, version, line_key, line_id"
            vals = f"'{self.name}', '{self.experiment_name}', '{self.version_name}', '{key}', {idx}"

            if key == self.buggy_line_key:
                cols += ", is_buggy_line"
                vals += ", TRUE"
            self.db.insert(
                "line_info",
                cols, vals
            )
    
    def add_cov_data(self, cov_data, tc_cov_json, tc_script_name, first=False):
        is_pass = False if tc_script_name in self.failing_tcs_list else True
        if tc_script_name not in cov_data["row_data"]:
            cov_data["row_data"][tc_script_name] = ""

        isCCTs = False
        if is_pass:
            if tc_script_name in self.passing_tcs_list:
                assert tc_script_name in self.passing_tcs_list, f"Test case {tc_script_name} is not in passing test cases"
            else:
                assert tc_script_name in self.ccts_list, f"Test case {tc_script_name} is not in CCTs"                
                isCCTs = True
        
        cnt = 0
        for file in tc_cov_json["files"]:
            filename = file["file"]
            # for each line in a given file
            for i in range(len(file["lines"])):
                line_data = file["lines"][i]

                lineno = line_data["line_number"]
                key = self.make_key(filename, lineno)

                # add key to the column data
                if first == True:
                    assert key not in cov_data["col_data"], f"Key {key} already exists in the row data"
                    cov_data["col_data"].append(key)
                    self.coverage_summary["num_total_lines"] += 1
                else:
                    assert key == cov_data["col_data"][cnt], f"Key {key} does not match with the col data key {cov_data['col_data'][cnt]}"


                covered = "1" if line_data["count"] > 0 else "0"
                cov_data["row_data"][tc_script_name] += covered

                if covered == "1":
                    # increment lines executed by test case
                    if key not in self.lines_execed:
                        self.lines_execed[key] = 0
                    self.lines_execed[key] += 1

                    if is_pass and isCCTs == False:
                        # increment lines executed by passing test case
                        if key not in self.lines_execed_by_passing_tc:
                            self.lines_execed_by_passing_tc[key] = []
                        self.lines_execed_by_passing_tc[key].append(tc_script_name)
                    elif is_pass and isCCTs == True:
                        # increment lines executed by ccts
                        if key not in self.lines_execed_by_ccts:
                            self.lines_execed_by_ccts[key] = []
                        self.lines_execed_by_ccts[key].append(tc_script_name)
                    else:
                        # increment lines executed by failing test case
                        if key not in self.lines_execed_by_failing_tc:
                            self.lines_execed_by_failing_tc[key] = []
                        self.lines_execed_by_failing_tc[key].append(tc_script_name)

                # assert that failing line executes buggy line
                # if is_pass == False and key == self.buggy_line_key:
                    # assert covered == "1", f"Failing test case {tc_script_name} does not execute buggy line {self.buggy_line_key}"
                    # print(f"Failing test case {tc_script_name} executes buggy line {self.buggy_line_key}")
                
                cnt += 1

    def add_key_data(self, cov_data, tc_cov_json):
        for file in tc_cov_json["files"]:
            filename = file["file"]
            for line in file["lines"]:
                lineno = line["line_number"]
                key = self.make_key(filename, lineno)
                
                assert key not in cov_data["col_data"], f"Key {key} already exists in the row data"
                cov_data["col_data"].append(key)
                self.coverage_summary["num_total_lines"] += 1

    
    def measure_coverage(self):
        """
        return 0 if success, 1 if failed to build, 2 if all passing TCs are CCTs
        """
        
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
        for tc_script_name in self.failing_tcs_list+self.passing_tcs_list+self.ccts_list:
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
            elif tc_script_name in self.passing_tcs_list:
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
        if len(self.ccts_list) > 0:
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
        special = "AND tc_name in (%s)" % ",".join(["'%s'" % tc for tc in self.ccts_list])
        self.db.update(
            "tc_info",
            set_values={"tc_result": "cct"},
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
                "version": self.version_name,
                "tc_result": "pass"
            },
            special=special
        )
        print(f">> CCTs are updated in the database")
    
   
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
            json.dump(perfile_line2function_data, f, ensure_ascii=False)
        
        return line2function_file