import json
import subprocess as sp

from lib.utils import *
from lib.experiment import Experiment

class Subject:
    def __init__(self, subject_name, stage_name):
        self.stage_name = stage_name
        self.name = subject_name

        self.work = work_dir / f"{subject_name}-{stage_name}"
        self.subject_dir = subjects_dir / subject_name
        self.subject_repo = self.work / subject_name
        self.config = self.read_configs()

        self.configure_file_position = self.work / self.config["configure_script_working_directory"]
        self.build_file_position = self.work / self.config["build_script_working_directory"]
        self.clean_build_file_position = self.work / self.config["build_script_working_directory"]

        self.compile_command_file = self.work / self.config["compile_command_path"]
        
        self.experiment = Experiment()

        self.initialize_working_directory()

    
    def read_configs(self):
        configs = None
        config_json = self.subject_dir / "configurations.json"
        
        with config_json.open() as f:
            configs = json.load(f)
        
        if configs is None:
            raise Exception("Configurations are not loaded")
        
        return configs
    
    def initialize_working_directory(self):
        # Copy self.subject_dir content to work_dir
        sp.check_call(["cp", "-r", self.subject_dir, self.work])
        
        configure_no_cov_file = self.work / "configure_no_cov_script.sh"
        configure_yes_cov_file = self.work / "configure_yes_cov_script.sh"
        build_file = self.work / "build_script.sh"
        clean_file = self.work / "clean_script.sh"

        assert configure_no_cov_file.exists(), "Configure script does not exist"
        assert configure_yes_cov_file.exists(), "Configure script does not exist"
        assert build_file.exists(), "Build script does not exist"
        assert clean_file.exists(), "Clean build script does not exist"

        sp.check_call(["cp", configure_no_cov_file, self.configure_file_position])
        sp.check_call(["cp", configure_yes_cov_file, self.configure_file_position])
        sp.check_call(["cp", build_file, self.build_file_position])
        sp.check_call(["cp", clean_file, self.clean_build_file_position])

        self.configure_no_cov_file = self.configure_file_position / "configure_no_cov_script.sh"
        self.configure_yes_cov_file = self.configure_file_position / "configure_yes_cov_script.sh"
        self.build_file = self.build_file_position / "build_script.sh"
        self.clean_file = self.clean_build_file_position / "clean_script.sh"
        
        assert self.configure_no_cov_file.exists(), "Configure script does not exist"
        assert self.configure_yes_cov_file.exists(), "Configure script does not exist"
        assert self.build_file.exists(), "Build script does not exist"
        assert self.clean_file.exists(), "Clean build script does not exist"
        
        if self.stage_name == "stage01":
            self.musicup_exec = self.copy_musicup()
        
        print(f"Initialized working directory: {self.work}")
    
    def copy_musicup(self):
        self.tools_dir = self.work / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        musicup_exec = tools_dir / "MUSICUP/music"
        
        sp.check_call(["cp", musicup_exec, self.tools_dir])

        return self.tools_dir / "music"
    
    def copy_exctractor(self):
        self.tools_dir = self.work / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        extractor_exec = tools_dir / "extractor/extractor"
        
        sp.check_call(["cp", extractor_exec, self.tools_dir])

        return self.tools_dir / "extractor"

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
        sp.check_call(
            ["bash", self.build_file],
            cwd=self.build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
    
    def clean_build(self):
        print(f">> Cleaning build for {self.name}")
        sp.check_call(
            ["bash", self.clean_file],
            cwd=self.clean_build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )
