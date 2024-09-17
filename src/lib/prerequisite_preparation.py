import time
import multiprocessing
import subprocess as sp
import random

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class PrerequisitePreparation(Subject):
    def __init__(
            self, subject_name, target_set_name,
            use_excluded_failing_tcs,
            passing_tcs_perc=1.0, failing_tcs_perc=1.0, verbose=False
        ):
        super().__init__(subject_name, "stage03", verbose)
        self.prerequisite_data_dir = out_dir / self.name / f"prerequisite_data"
        self.prerequisite_data_dir.mkdir(exist_ok=True)

        self.use_excluded_failing_tcs = use_excluded_failing_tcs

        self.passing_tcs_perc = passing_tcs_perc
        self.failing_tcs_perc = failing_tcs_perc

        self.fileManager = FileManager(self.name, self.work, self.verbose)

        self.target_set_dir = out_dir / self.name / target_set_name
        assert self.target_set_dir.exists(), "Origin set directory does not exist"

        self.allPassisCCTdir = out_dir / f"{self.name}" / "allPassisCCT"
        self.allPassisCCTdir.mkdir(exist_ok=True, parents=True)
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()

        # 2. get versions from target_set_dir
        self.versions_list = get_dirs_in_dir(self.target_set_dir)

        # 4. Assign versions to machines
        self.versions_assignments = self.assign_works_to_machines(self.versions_list)

        # 5. Prepare for testing versions
        self.prepare_for_testing_versions()

        # 6. Test versions
        self.test_versions()

    
    # +++++++++++++++++++++++++++
    # ++++++ Testing stage ++++++
    # +++++++++++++++++++++++++++    
    def test_versions(self):
        if self.experiment.experiment_config["use_distributed_machines"]:
            self.test_versions_remote()
        else:
            self.test_versions_local()
    
    def test_versions_remote(self):
        jobs = []
        for machine_core, versions in self.versions_assignments.items():
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_remote,
                args=(machine, core, homedir, versions)
            )
            jobs.append(job)
            job.start()
            time.sleep(0.5) # to avoid ssh connection error

        for job in jobs:
            job.join()
        
        print(f">> Finished testing all versions now retrieving versions with its prerequisite data")
        self.fileManager.collect_data_remote("prerequisite_data", self.prerequisite_data_dir, self.versions_assignments)
        self.fileManager.collect_data_remote("allPassisCCT", self.allPassisCCTdir, self.versions_assignments)
    
    def test_single_machine_core_remote(self, machine, core, homedir, versions):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        for version in versions:
            version_name = version.name

            optional_flag = ""
            if need_configure:
                optional_flag = "--need-configure"
                need_configure = False
            if self.use_excluded_failing_tcs:
                optional_flag += " --use-excluded-failing-tcs"
            if self.passing_tcs_perc != 1.0:
                optional_flag += f" --passing-tcs-perc {self.passing_tcs_perc}"
            if self.failing_tcs_perc != 1.0:
                optional_flag += f" --failing-tcs-perc {self.failing_tcs_perc}"
            if self.verbose:
                optional_flag += " --verbose"

            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_prerequisites.py --subject {subject_name} --machine {machine_name} --core {core_name} --version {version_name} {optional_flag}"
            ]
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {version.name} +++++\n")
                f.write("+++++ STDOUT +++++\n")
                f.write(res.stdout.decode())
                f.write("\n+++++ STDERR +++++\n")
                f.write(res.stderr.decode())
    
    def test_versions_local(self):
        jobs = []
        for machine_core, versions in self.versions_assignments.items():
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_local,
                args=(machine, core, homedir, versions)
            )
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()

    def test_single_machine_core_local(self, machine, core, homedir, versions):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        for version in versions:
            version_name = version.name
            
            cmd = [
                "python3", "test_version_prerequisites.py",
                "--subject", subject_name, "--machine", machine_name, "--core", core_name,
                "--version", version_name
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if self.use_excluded_failing_tcs:
                cmd.append("--use-excluded-failing-tcs")
            if self.passing_tcs_perc != 1.0:
                cmd.append("--passing-tcs-perc")
                cmd.append(str(self.passing_tcs_perc))
            if self.failing_tcs_perc != 1.0:
                cmd.append("--failing-tcs-perc")
                cmd.append(str(self.failing_tcs_perc))
            if self.verbose:
                cmd.append("--verbose")
            
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=src_dir)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {version.name} +++++\n")
                f.write("+++++ STDOUT +++++\n")
                f.write(res.stdout.decode())
                f.write("\n+++++ STDERR +++++\n")
                f.write(res.stderr.decode())


    # +++++++++++++++++++++++++++++
    # ++++++ Preparing stage ++++++
    # +++++++++++++++++++++++++++++
    def prepare_for_testing_versions(self):
        if self.experiment.experiment_config["use_distributed_machines"]:
            self.prepare_for_remote()
        else:
            self.prepare_for_local()
    
    def prepare_for_remote(self):
        self.fileManager.make_assigned_works_dir_remote(self.experiment.machineCores_list, self.stage_name)
        self.fileManager.send_works_remote(self.versions_assignments, self.stage_name)
        
        self.fileManager.send_repo_remote(self.subject_repo, self.experiment.machineCores_list)

        self.fileManager.send_configurations_remote(self.experiment.machineCores_dict)
        self.fileManager.send_src_remote(self.experiment.machineCores_dict)
        self.fileManager.send_tools_remote(self.tools_dir, self.experiment.machineCores_dict)
        self.fileManager.send_experiment_configurations_remote(self.experiment.machineCores_dict)
    
    def prepare_for_local(self):
        self.working_env = self.fileManager.make_working_env_local()

        for machine_core, versions in self.versions_assignments.items():
            # versions is list of directory path to versions
            machine, core, homedir = machine_core.split("::")
            machine_core_dir = self.working_env / machine / core
            assigned_dir = machine_core_dir / f"{self.stage_name}-assigned_works"
            assigned_dir.mkdir(exist_ok=True, parents=True)

            for version in versions:
                print_command(["cp", "-r", version, assigned_dir], self.verbose)
                sp.check_call(["cp", "-r", version, assigned_dir])
            
            core_repo_dir = machine_core_dir / f"{self.name}"
            if not core_repo_dir.exists():
                print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
                sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])
