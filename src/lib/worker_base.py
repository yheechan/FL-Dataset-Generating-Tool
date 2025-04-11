import json
import subprocess as sp
import os
from pathlib import Path

from lib.utils import *
from lib.experiment import Experiment

class Worker:
    def __init__(self, subject_name, stage_name, worker_env_name, machine, core, verbose=False):
        self.name = subject_name
        self.stage_name = stage_name
        self.worker_env_name = worker_env_name # This can be deleted
        self.machine = machine
        self.core = core
        self.verbose = verbose

        self.work = work_dir / f"{self.name}"
        self.tools_dir = self.work / "tools"
        self.core_dir = self.work / f"working_env/{machine}/{core}"
        self.subject_repo = self.work / self.name
        self.config = self.read_configs()

        self.configure_file_position = self.core_dir / self.config["configure_script_working_directory"]
        self.build_file_position = self.core_dir / self.config["build_script_working_directory"]
        self.clean_build_file_position = self.core_dir / self.config["build_script_working_directory"]
        
        self.compile_command_file = self.core_dir / self.config["compile_command_path"]
        self.subject_lang = self.config["subject_language"]

        # configure and build files
        self.configure_no_cov_file = self.configure_file_position / "configure_no_cov_script.sh"
        self.configure_yes_cov_file = self.configure_file_position / "configure_yes_cov_script.sh"
        self.build_file = self.build_file_position / "build_script.sh"
        self.clean_file = self.clean_build_file_position / "clean_script.sh"
        assert self.configure_no_cov_file.exists(), f"Configure no cov file does not exist: {self.configure_no_cov_file}"
        assert self.configure_yes_cov_file.exists(), f"Configure yes cov file does not exist: {self.configure_yes_cov_file}"
        assert self.build_file.exists(), f"Build file does not exist: {self.build_file}"
        assert self.clean_file.exists(), f"Clean file does not exist: {self.clean_file}"

        # test case directory
        self.testsuite_dir = self.core_dir / self.config["test_case_directory"]

        # set environment variables
        self.experiment = Experiment()
        self.max_mutants = self.experiment.experiment_config["max_mutants"]
        self.number_of_lines_to_mutation_test = self.experiment.experiment_config["number_of_lines_to_mutation_test"]

        self.gcovr_exec = Path(self.experiment.experiment_config["abs_path_to_gcovr_executable"]).expanduser()

        self.log = log_dir / f"{self.name}/{self.stage_name}" # 2024-08-13 implement parallel mode
        self.log.mkdir(exist_ok=True, parents=True)

    def read_configs(self):
        configs = None
        config_json = self.subject_repo / "configurations.json"
        
        with config_json.open() as f:
            configs = json.load(f)
        
        if configs is None:
            raise Exception("Configurations are not loaded")
        
        return configs

    # +++++++++++++++++++++++++++++++++
    # ++++++ Configure & Build ++++++++
    # +++++++++++++++++++++++++++++++++
    def configure_no_cov(self):
        print(f">> Configuring {self.name} without coverage")
        print_command(["bash", self.configure_no_cov_file], self.verbose)
        res = sp.run(
            ["bash", self.configure_no_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
        return res.returncode
    
    def configure_yes_cov(self):
        print(f">> Configuring {self.name} with coverage")
        print_command(["bash", self.configure_yes_cov_file], self.verbose)
        sp.check_call(
            ["bash", self.configure_yes_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def build(self, piping=True):
        print(f">> Building {self.name}")
        print_command(["bash", self.build_file], self.verbose)
        if piping:
            res = sp.run(
                ["bash", self.build_file],
                cwd=self.build_file_position,
                stderr=sp.PIPE, stdout=sp.PIPE
            )
            return res.returncode
        else:
            res = sp.run(
                ["bash", self.build_file],
                cwd=self.build_file_position,
            )
            return res.returncode
    
    def clean_build(self):
        print(f">> Cleaning build for {self.name}")
        print_command(["bash", self.clean_file], self.verbose)
        res = sp.run(
            ["bash", self.clean_file],
            cwd=self.clean_build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )

    # +++++++++++++++++++++++++++++
    # ++++++ Patch & Test +++++++++
    # +++++++++++++++++++++++++++++
    def make_patch_file(self, target_file, version_file, patch_file_name):
        patch_file = self.core_dir / patch_file_name
        assert target_file.exists(), f"Target file does not exist: {target_file}"
        assert version_file.exists(), f"Mutant file does not exist: {version_file}"
        print_command(["diff", target_file.__str__(), version_file.__str__()], self.verbose)
        sp.run(
            ["diff", target_file.__str__(), version_file.__str__()],
            stdout=patch_file.open("w"),
        )
        return patch_file

    def apply_patch(self, target_file, version_file, patch_file, is_revert):
        if is_revert:
            print_command(
                ["patch", "-R", "-i", patch_file.__str__(), target_file.__str__()],
                self.verbose
            )
            sp.check_call(
                ["patch", "-R", "-i", patch_file.__str__(), target_file.__str__()],
                stderr=sp.PIPE, stdout=sp.PIPE
            )
            print(f">> Reverted {target_file.name} to original from {version_file.name}")
        else:
            print_command(
                ["patch", "-i", patch_file.__str__(), target_file.__str__()],
                self.verbose
            )
            sp.check_call(
                ["patch", "-i", patch_file.__str__(), target_file.__str__()],
                stderr=sp.PIPE, stdout=sp.PIPE
            )
            print(f">> Applied patch to {target_file.name} with {version_file.name}")
    
    def run_test_case(self, tc_script):
        res = sp.run(
            f"./{tc_script}",
            shell=True, cwd=self.testsuite_dir,
            stderr=sp.PIPE, stdout=sp.PIPE,
            env=self.my_env
        )
        # rm -rf log/*
        # rm -rf exe/log/*
        # 2024-08-14 SPECIFICALLY WRITTEN FOR NSFW C LANGUAGE
        # sp.run("rm -rf log/*", shell=True,
        #         cwd=self.testsuite_dir.parent.parent.parent,
        #         stderr=sp.PIPE, stdout=sp.PIPE,
        #         env=self.my_env
        # )
        # sp.run("rm -rf exe/log/*", shell=True,
        #         cwd=self.testsuite_dir.parent.parent.parent,
        #         stderr=sp.PIPE, stdout=sp.PIPE,
        #         env=self.my_env
        # )
        return res.returncode

    def set_env(self):
        # set environment variables
        self.my_env = os.environ.copy()
        if self.config["environment_setting"]["needed"] == True:
            for key, value in self.config["environment_setting"]["variables"].items():
                path = self.core_dir / value
                assert path.exists(), f"Path {path} does not exist"
                path_str = path.__str__()

                if key not in self.my_env:
                    self.my_env[key] = path_str
                else:
                    self.my_env[key] = f"{path_str}:{self.my_env[key]}"
    

    # ++++++++++++++++++++++++++
    # ++++++ Version Info ++++++
    # ++++++++++++++++++++++++++
    def set_testcases(self, version_dir):
        self.failing_tcs_list = get_tc_list(version_dir / "testsuite_info" / "failing_tcs.txt")
        self.passing_tcs_list = get_tc_list(version_dir / "testsuite_info" / "passing_tcs.txt")
        self.excluded_failing_tcs_list = get_tc_list(version_dir / "testsuite_info" / "excluded_failing_tcs.txt")
        self.excluded_passing_tcs_list = get_tc_list(version_dir / "testsuite_info" / "excluded_passing_tcs.txt")
        self.ccts_list = get_tc_list(version_dir / "testsuite_info" / "ccts.txt")

    def set_line2function_dict(self, version_dir):
        line2function_file = version_dir / "line2function_info" / "line2function.json"
        assert line2function_file.exists(), f"Line2function file does not exist: {line2function_file}"

        with line2function_file.open() as f:
            line2function_dict = json.load(f)

        self.line2function_dict = line2function_dict
    
    def make_key(self, target_code_file, buggy_lineno):
        if int(buggy_lineno) == -1:
            return "UNKNOWN#UNKOWN#-1"
        # filename = target_code_file_path.split('/')[-1]
        filename = target_code_file
        function = None
        for key, value in self.line2function_dict.items():
            if key.endswith(filename):
                for func_info in value:
                    if int(func_info[1]) <= int(buggy_lineno) <= int(func_info[2]):
                        function = f"{filename}#{func_info[0]}#{buggy_lineno}"
                        return function
        function = f"{filename}#FUNCTIONNOTFOUND#{buggy_lineno}"
        return function
    
    def set_lines_executed_by_failing_tc(self, version_dir, target_code_file, buggy_lineno):
        lines_executed_by_failing_tc_file = version_dir / "coverage_info" / "lines_executed_by_failing_tc.json"
        assert lines_executed_by_failing_tc_file.exists(), f"Lines executed by failing tc file does not exist: {lines_executed_by_failing_tc_file}"

        lines_executed_by_failing_tc_json = json.loads(lines_executed_by_failing_tc_file.read_text())

        executed_lines = {}
        for target_file in self.config["target_files"]:
            # filename = target_file.split("/")[-1]
            filename = target_file # FILENAME STRUCTURE! 20240925
            executed_lines[filename] = {}
        
        buggy_filename = target_code_file # FILENAME STRUCTURE! 20240925
        executed_buggy_line = False
        for key, tcs_list in lines_executed_by_failing_tc_json.items():
            info = key.split("#")
            # filename = info[0].split("/")[-1]
            filename = info[0] # FILENAME STRUCTURE! 20240925
            function_name = info[1]
            lineno = info[2]

            if filename not in executed_lines:
                executed_lines[filename] = {}
            
            if lineno not in executed_lines[filename]:
                executed_lines[filename][lineno] = []

            executed_lines[filename][lineno] = tcs_list

            if filename == buggy_filename and int(lineno) == int(buggy_lineno):
                executed_buggy_line = True
        
        if int(buggy_lineno) != -1:
            assert executed_buggy_line, f"Buggy line {buggy_lineno} is not executed by any failing test case"
        self.lines_executed_by_failing_tcs = executed_lines
        
        
    
    # ++++++++++++++++++++++++++++++
    # ++++++ Coverage Related ++++++
    # ++++++++++++++++++++++++++++++
    def set_target_preprocessed_files(self):
        self.target_preprocessed_files = self.config["target_preprocessed_files"]
    
    def set_filtered_files_for_gcovr(self):
        self.targeted_files = self.config["target_files"]
        # self.targeted_files = [file.split("/")[-1] for file in self.targeted_files]
        self.targeted_files = [file for file in self.targeted_files]
        # filtered_targeted_files = ["(.+/)?"+file.__str__()+"$" for file in filtered_targeted_files]
        filtered_targeted_files = [self.core_dir / file for file in self.targeted_files]
        filtered_targeted_files = [file.__str__() for file in filtered_targeted_files]
        self.filtered_files = "|".join(filtered_targeted_files) + "$"

        self.target_gcno_gcda = []
        for target_file in self.targeted_files:
            target_file = target_file.split("/")[-1]
            if self.subject_lang == "C":
                # get filename without extension
                # remember the filename can be x.y.cpp
                filename = ".".join(target_file.split(".")[:-1]) + "*"
            else:
                filename = ".".join(target_file.split(".")[:-1]) + ".cpp"
            gcno_file = "*" + filename + ".gcno"
            gcda_file = "*" + filename + ".gcda"
            self.target_gcno_gcda.append(gcno_file)
            self.target_gcno_gcda.append(gcda_file)
    
    def remove_all_gcda(self, core_repo_dir):
        cmd = [
            "find", ".", "-type", "f",
            "-name", "*.gcda", "-delete"
        ]
        sp.check_call(cmd, cwd=core_repo_dir, stderr=sp.PIPE, stdout=sp.PIPE)

    def remove_untargeted_files_for_gcovr(self, core_repo_dir):
        cmd = [
            "find", ".", "-type", "f",
            "(", "-name", "*.gcno", "-o", "-name", "*.gcda", ")"
        ]

        for target_file in self.target_gcno_gcda:
            cmd.extend(["!", "-name", target_file])
        cmd.extend(["-delete"])
        print_command(cmd, self.verbose)
        sp.check_call(cmd, cwd=core_repo_dir, stderr=sp.PIPE, stdout=sp.PIPE)
    
    def generate_coverage_json(self, core_repo_dir, cov_dir, tc_script_name):
        tc_name = tc_script_name.split(".")[0]
        file_name = f"{tc_name}.raw.json"
        raw_cov_file = cov_dir / file_name
        raw_cov_file = raw_cov_file.resolve()
        cmd = [self.gcovr_exec.__str__()]
        if self.config["cov_compiled_with_clang"] == True:
            cmd.extend(["--gcov-executable", "llvm-cov gcov"])
            cov_cwd=core_repo_dir
        else:
            obj_dir = self.core_dir / self.config["gcovr_object_root"]
            src_root_dir = self.core_dir / self.config["gcovr_source_root"]
            if self.experiment.experiment_config["gcovr_version"] < 7.2:
                cmd.extend([
                    "--object-directory", obj_dir.__str__(),
                    "--root", src_root_dir.__str__(),
                ])
            else:
                cmd.extend([
                    "--gcov-object-directory", obj_dir.__str__(),
                    "--root", src_root_dir.__str__(),
                ])
            cov_cwd=obj_dir
        cmd.extend([
            "--filter", self.filtered_files,
            "--json", "-o", raw_cov_file.__str__(),
            "--gcov-ignore-parse"
        ])
        print_command(cmd, self.verbose)
        sp.check_call(cmd, cwd=cov_cwd, stderr=sp.PIPE, stdout=sp.PIPE)
        return raw_cov_file

    def check_buggy_line_covered(self, tc_script_name, raw_cov_file, target_file, buggy_lineno):
        if int(buggy_lineno) == -1:
            return 0

        with raw_cov_file.open() as f:
            cov_data = json.load(f)
        
        # target_file = target_file.name

        # filename_list = [file["file"].split("/")[-1] for file in cov_data["files"]]

        # if target_file not in filename_list:
        #     return -2
        
        file_exists = False
        for file in cov_data["files"]:
            if target_file in file["file"]:
                file_exists = True
                break
        
        if not file_exists:
            return -2
        
        for file in cov_data["files"]:
            # filename = file["file"].split("/")[-1]
            # if filename == target_file:
            filename = file["file"]
            if target_file in filename:
                lines = file["lines"]
                for line in lines:
                    if line["line_number"] == int(buggy_lineno):
                        cur_lineno = line["line_number"]
                        cur_count = line["count"]
                        print(f"{tc_script_name} on line {cur_lineno} has count: {cur_count}")
                        if line["count"] > 0:
                            return 0
                        else:
                            return 1
                return 1
        return 1
    
    def get_lines_from_pp_cov(self, pp_cov_file):
        lines_list = []
        with open(pp_cov_file, "r") as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            for row in csv_reader:
                lines_list.append(row[0])
        return lines_list
    
    def get_lines_from_pp_cov_as_dict(self, pp_cov_file, noCCTs=False):
        tc_list = self.failing_tcs_list + self.passing_tcs_list + self.ccts_list
        if noCCTs:
            tc_list = self.failing_tcs_list + self.passing_tcs_list

        cov_per_line = []
        check_tc_col = True
        buggy_line_exists = False
        with open(pp_cov_file, "r") as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                line_key = row["key"]

                if line_key == self.buggy_line_key or int(self.buggy_lineno) == -1:
                    buggy_line_exists = True

                cov_per_line.append(row)

                # VALIDATE: pp cov data has all tcs
                if check_tc_col:
                    for tc in tc_list:
                        tc_name = tc.split(".")[0]
                        if tc_name not in row:
                            raise Exception(f"Test case {tc_name} is not in coverage data")
                    check_tc_col = False
        assert buggy_line_exists, f"Buggy line {self.buggy_line_key} does not exist in postprocessed coverage data"
        return cov_per_line

    # +++++++++++++++++++++++++++
    # ++++++ Commons Info++++++++
    # +++++++++++++++++++++++++++
    def get_bug_info(self, target_dir):
        bug_info_csv = target_dir / "bug_info.csv"
        assert bug_info_csv.exists(), f"Bug info csv does not exist: {bug_info_csv}"

        with open(bug_info_csv, "r") as f:
            lines = f.readlines()
            target_code_file, mutant_code_file, buggy_lineno = lines[1].strip().split(",")

        # 2024-09-18 changed to not return path
        # target_code_file = self.core_dir / target_code_file
        # assert target_code_file.exists(), f"Target code file does not exist: {target_code_file}"
        
        return target_code_file, mutant_code_file, buggy_lineno

    def get_buggy_code_file(self, target_dir, code_filename):
        buggy_code_file = target_dir / "buggy_code_file" / code_filename
        assert buggy_code_file.exists(), f"Buggy code file does not exist: {buggy_code_file}"
        return buggy_code_file

    def save_version(self, version_dir, destination_dir):
        print(f">> Saving version {version_dir.name} to {destination_dir}")
        print_command(["cp", "-r", version_dir, destination_dir], self.verbose)
        sp.check_call(["cp", "-r", version_dir, destination_dir])
