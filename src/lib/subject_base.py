import json
import subprocess as sp
import shutil

from lib.utils import *
from lib.experiment import Experiment
from lib.database import CRUD
from lib.file_manager import FileManager

class Subject:
    def __init__(self, subject_name, stage_name, verbose=False):
        self.stage_name = stage_name
        self.name = subject_name
        self.verbose = verbose

        self.work = work_dir / f"{subject_name}"
        self.subject_dir = subjects_dir / subject_name
        self.subject_repo = self.work / subject_name
        self.config = self.read_configs()

        self.configure_file_position = self.work / self.config["configure_script_working_directory"]
        self.build_file_position = self.work / self.config["build_script_working_directory"]
        self.clean_build_file_position = self.work / self.config["build_script_working_directory"]

        self.compile_command_file = self.work / self.config["compile_command_path"]
        self.real_world_buggy_versions_status = self.config["real_world_buggy_versions"]
        
        self.experiment = Experiment()

        self.out = out_dir / f"{self.name}"
        self.out.mkdir(exist_ok=True, parents=True)

        self.log = log_dir / f"{self.name}/{self.stage_name}"
        self.log.mkdir(exist_ok=True, parents=True)

    def connect_to_db(self):
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
    
    def get_works(self, generated_mutants_dir, experiment_name, special=""):
        res = self.db.read(
            "bug_info",
            columns="version, type, target_code_file, buggy_code_file",
            conditions={
                "subject": self.name,
                "experiment_name": experiment_name,
            },
            special=special
        )

        # work_list = [(version, buggy_code_file_path), ...]
        work_list = []
        for row in res:
            version = row[0]
            version_type = row[1]
            target_code_file = row[2]
            buggy_code_file = row[3]

            target_file_mutant_dir_name = target_code_file.replace("/", "#")
            target_file_mutant_dir = generated_mutants_dir / target_file_mutant_dir_name

            if version_type == "real_world":
                buggy_code_file_path = self.work / f"real_world_buggy_versions/{version}/buggy_code_file/{buggy_code_file}"
            else:
                assert target_file_mutant_dir.exists(), "Target file mutant directory does not exist"
                buggy_code_file_path = target_file_mutant_dir / buggy_code_file
            
            assert buggy_code_file_path.exists(), "Buggy code file does not exist"

            work_list.append((version, buggy_code_file_path))

        return work_list
    
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
        source = self.subject_dir.__str__() + "/."
        print_command(["cp", "-r", source, self.work], self.verbose)
        sp.check_call(["cp", "-r", source, self.work])
        
        configure_no_cov_file = self.work / "configure_no_cov_script.sh"
        configure_yes_cov_file = self.work / "configure_yes_cov_script.sh"
        build_file = self.work / "build_script.sh"
        clean_file = self.work / "clean_script.sh"

        assert configure_no_cov_file.exists(), "Configure script does not exist"
        assert configure_yes_cov_file.exists(), "Configure script does not exist"
        assert build_file.exists(), "Build script does not exist"
        assert clean_file.exists(), "Clean build script does not exist"

        print_command(["cp", configure_no_cov_file, self.configure_file_position], self.verbose)
        sp.check_call(["cp", configure_no_cov_file, self.configure_file_position])
        print_command(["cp", configure_yes_cov_file, self.configure_file_position], self.verbose)
        sp.check_call(["cp", configure_yes_cov_file, self.configure_file_position])
        print_command(["cp", build_file, self.build_file_position], self.verbose)
        sp.check_call(["cp", build_file, self.build_file_position])
        print_command(["cp", clean_file, self.clean_build_file_position], self.verbose)
        sp.check_call(["cp", clean_file, self.clean_build_file_position])

        self.configure_no_cov_file = self.configure_file_position / "configure_no_cov_script.sh"
        self.configure_yes_cov_file = self.configure_file_position / "configure_yes_cov_script.sh"
        self.build_file = self.build_file_position / "build_script.sh"
        self.clean_file = self.clean_build_file_position / "clean_script.sh"
        
        assert self.configure_no_cov_file.exists(), "Configure script does not exist"
        assert self.configure_yes_cov_file.exists(), "Configure script does not exist"
        assert self.build_file.exists(), "Build script does not exist"
        assert self.clean_file.exists(), "Clean build script does not exist"
        
        self.musicup_exec = self.copy_musicup()
        self.extractor_exec = self.copy_extractor()
        
        print(f"Initialized working directory: {self.work}")
    
    def copy_musicup(self):
        self.tools_dir = self.work / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        musicup_exec = tools_dir / "MUSICUP/music"
        
        print_command(["cp", musicup_exec, self.tools_dir], self.verbose)
        sp.check_call(["cp", musicup_exec, self.tools_dir])

        return self.tools_dir / "music"
    
    def copy_extractor(self):
        self.tools_dir = self.work / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        extractor_exec = tools_dir / "extractor/extractor"
        
        print_command(["cp", extractor_exec, self.tools_dir], self.verbose)
        sp.check_call(["cp", extractor_exec, self.tools_dir])

        return self.tools_dir / "extractor"

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
    
    def build(self, piping=True):
        print(f">> Building {self.name}")
        print_command(["bash", self.build_file], self.verbose)

        if piping:
            sp.call(
                ["bash", self.build_file],
                cwd=self.build_file_position,
                stderr=sp.PIPE, stdout=sp.PIPE
            )
        else:
            sp.check_call(
                ["bash", self.build_file],
                cwd=self.build_file_position
            )
    
    def clean_build(self):
        print(f">> Cleaning build for {self.name}")
        print_command(["bash", self.clean_file], self.verbose)
        sp.check_call(
            ["bash", self.clean_file],
            cwd=self.clean_build_file_position,
            stderr=sp.PIPE, stdout=sp.PIPE    
        )

    def assign_works_to_machines(self, work_list):
        # returns a dict with format of
        # {machine::core::homdir": [(version_name, code_path), ...]}
        work_assignments = {}
        for idx, work_info in enumerate(work_list):
            machine_core = self.experiment.machineCores_list[idx % len(self.experiment.machineCores_list)]

            machine_core_str = "::".join(machine_core)

            if machine_core_str not in work_assignments:
                work_assignments[machine_core_str] = []

            work_assignments[machine_core_str].append(work_info)
        return work_assignments


    def prepare_for_local(self, fileManager, versions_assignments, dir_form=False):
        self.working_env = fileManager.make_working_env_local()

        for machine_core, work_infos in versions_assignments.items():
            # versions is list of directory path to versions
            machine, core, homedir = machine_core.split("::")
            machine_core_dir = self.working_env / machine / core
            assigned_dir = machine_core_dir / f"{self.stage_name}-assigned_works"
            assigned_dir.mkdir(exist_ok=True, parents=True)

            if dir_form:
                for version_dir in work_infos:
                    print_command(["cp", "-r", version_dir, assigned_dir], self.verbose)
                    sp.check_call(["cp", "-r", version_dir, assigned_dir])
            else:
                for version_name, code_path in work_infos:
                    version_dir = assigned_dir / version_name / "buggy_code_file"
                    print_command(["mkdir", "-p", version_dir], self.verbose)
                    version_dir.mkdir(exist_ok=True, parents=True)
                    # copy buggy code file to version_dir
                    print_command(["cp", code_path, version_dir], self.verbose)
                    sp.check_call(["cp", code_path, version_dir])
                
            core_repo_dir = machine_core_dir / f"{self.name}"
            if core_repo_dir.exists():
                shutil.rmtree(core_repo_dir)

            print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
            sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])

    def prepare_for_remote(self, fileManager:FileManager, versions_assignments, dir_form=False):
        fileManager.make_assigned_works_dir_remote(self.experiment.machineCores_list, self.stage_name)
        fileManager.send_works_remote(versions_assignments, self.stage_name, dir_form=dir_form)
        
        fileManager.send_repo_remote(self.subject_repo, self.experiment.machineCores_list)

        fileManager.send_configurations_remote(self.experiment.machineCores_dict)
        fileManager.send_src_remote(self.experiment.machineCores_dict)
        fileManager.send_tools_remote(self.tools_dir, self.experiment.machineCores_dict)
        fileManager.send_experiment_configurations_remote(self.experiment.machineCores_dict)

    def get_bug_idx(self, subject_name, experiment_name, version_name):
        res = self.db.read(
            "bug_info",
            columns="bug_idx",
            conditions={
                "subject": subject_name,
                "experiment_name": experiment_name,
                "version": version_name
            }
        )
        assert len(res) == 1, f"Bug info does not exist for {version_name}"
        return res[0][0]