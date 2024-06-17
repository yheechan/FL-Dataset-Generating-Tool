import json
import subprocess as sp
import os
from pathlib import Path

from lib.utils import *

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

        self.gcovr_exec = Path("~/.local/bin/gcovr").expanduser()

    def read_configs(self):
        configs = None
        config_json = self.work / "configurations.json"
        
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
        sp.check_call(
            ["bash", self.configure_no_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def configure_yes_cov(self):
        print(f">> Configuring {self.name} with coverage")
        print_command(["bash", self.configure_yes_cov_file], self.verbose)
        sp.check_call(
            ["bash", self.configure_yes_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def build(self):
        print(f">> Building {self.name}")
        print_command(["bash", self.build_file], self.verbose)
        res = sp.run(
            ["bash", self.build_file],
            cwd=self.build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE
        )
        return res.returncode
    
    def clean_build(self):
        print(f">> Cleaning build for {self.name}")
        print_command(["bash", self.clean_file], self.verbose)
        sp.check_call(
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
    

    # ++++++++++++++++++++++++++++++
    # ++++++ Coverage Related ++++++
    # ++++++++++++++++++++++++++++++
    def set_filtered_files_for_gcovr(self):
        self.targeted_files = self.config["target_files"]
        self.targeted_files = [file.split("/")[-1] for file in self.targeted_files]
        self.filtered_files = "|".join(self.targeted_files)

        self.target_gcno_gcda = []
        for target_file in self.targeted_files:
            filename = target_file.split(".")[0]
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
        sp.check_call(cmd, cwd=core_repo_dir, stderr=sp.PIPE, stdout=sp.PIPE)
    
    def generate_coverage_json(self, core_repo_dir, cov_dir, tc_script_name):
        tc_name = tc_script_name.split(".")[0]
        file_name = f"{tc_name}.raw.json"
        raw_cov_file = cov_dir / file_name
        raw_cov_file = raw_cov_file.resolve()
        cmd = [
            self.gcovr_exec.__str__(),
            "--filter", self.filtered_files,
            "--gcov-executable", "llvm-cov gcov",
            "--json", "-o", raw_cov_file.__str__()
        ]
        sp.check_call(cmd, cwd=core_repo_dir, stderr=sp.PIPE, stdout=sp.PIPE)
        return raw_cov_file

    def check_buggy_line_covered(self, tc_script_name, raw_cov_file, target_file, buggy_lineno):
        with raw_cov_file.open() as f:
            cov_data = json.load(f)
        
        target_file = target_file.name

        filename_list = [file["file"] for file in cov_data["files"]]

        if target_file not in filename_list:
            return -2
        
        for file in cov_data["files"]:
            if file["file"] == target_file:
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

    # +++++++++++++++++++++++++++
    # ++++++ Commons Info++++++++
    # +++++++++++++++++++++++++++
    def get_tc_list(self, target_dir, type):
        tc_file = target_dir / "testsuite_info" / type
        assert tc_file.exists(), f"Test case file does not exist: {tc_file}"

        tc_list = []
        with tc_file.open() as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    tc_list.append(line)
        
        tc_list = sorted(tc_list, key=sort_testcase_script_name)
        return tc_list

    def get_bug_info(self, target_dir):
        bug_info_csv = target_dir / "bug_info.csv"
        assert bug_info_csv.exists(), f"Bug info csv does not exist: {bug_info_csv}"

        with open(bug_info_csv, "r") as f:
            lines = f.readlines()
            target_code_file, mutant_code_file, buggy_lineno = lines[1].strip().split(",")

        target_code_file = self.core_dir / target_code_file
        assert target_code_file.exists(), f"Target code file does not exist: {target_code_file}"
        
        return target_code_file, mutant_code_file, buggy_lineno

    def get_buggy_code_file(self, target_dir, code_filename):
        buggy_code_file_dir = target_dir / "buggy_code_file"
        buggy_code_file = buggy_code_file_dir / code_filename
        assert buggy_code_file.exists(), f"Buggy code file does not exist: {buggy_code_file}"
        return buggy_code_file
