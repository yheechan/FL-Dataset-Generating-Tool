import json
import subprocess as sp
import os

from lib.utils import *

class Worker:
    def __init__(self, subject_name, stage_name, worker_env_name, machine, core):
        self.name = subject_name
        self.stage_name = stage_name
        self.worker_env_name = worker_env_name
        self.machine = machine
        self.core = core

        self.work = work_dir / f"{self.name}-{stage_name}"
        self.tools_dir = self.work / "tools"
        self.core_dir = self.work / f"workers-{worker_env_name}/{machine}/{core}"
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

    def read_configs(self):
        configs = None
        config_json = self.work / "configurations.json"
        
        with config_json.open() as f:
            configs = json.load(f)
        
        if configs is None:
            raise Exception("Configurations are not loaded")
        
        return configs

    def configure_no_cov(self):
        print(f">> Configuring {self.name} without coverage")
        sp.check_call(
            ["bash", self.configure_no_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def configure_yes_cov(self):
        print(f">> Configuring {self.name} with coverage")
        sp.check_call(
            ["bash", self.configure_yes_cov_file],
            cwd=self.configure_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def build(self):
        print(f">> Building {self.name}")
        res = sp.run(
            ["bash", self.build_file],
            cwd=self.build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE
        )
        return res.returncode
    
    def clean_build(self):
        print(f">> Cleaning build for {self.name}")
        sp.check_call(
            ["bash", self.clean_file],
            cwd=self.clean_build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )

    def make_patch_file(self, target_file, mutant_file, patch_file_name):
        patch_file = self.core_dir / patch_file_name
        assert target_file.exists(), f"Target file does not exist: {target_file}"
        assert mutant_file.exists(), f"Mutant file does not exist: {mutant_file}"
        sp.run(
            ["diff", target_file.__str__(), mutant_file.__str__()],
            stdout=patch_file.open("w"),
        )
        return patch_file

    def apply_patch(self, target_file, mutant_file, patch_file, is_revert):
        if is_revert:
            sp.check_call(
                ["patch", "-R", "-i", patch_file.__str__(), target_file.__str__()],
                stderr=sp.PIPE, stdout=sp.PIPE
            )
            print(f">> Reverted {target_file.name} to original from {mutant_file.name}")
        else:
            sp.check_call(
                ["patch", "-i", patch_file.__str__(), target_file.__str__()],
                stderr=sp.PIPE, stdout=sp.PIPE
            )
            print(f">> Applied patch to {target_file.name} with {mutant_file.name}")
    
    def run_test_case(self, tc_script):
        res = sp.run(
            f"./{tc_script}",
            shell=True, cwd=self.testsuite_dir,
            stderr=sp.PIPE, stdout=sp.PIPE,
            env=self.my_env
        )
        return res.returncode
