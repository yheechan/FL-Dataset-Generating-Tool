import time
import multiprocessing
import subprocess as sp
import random

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class UsableVersionSelection(Subject):
    def __init__(self, subject_name, experiment_name, verbose=False):
        super().__init__(subject_name, "stage02", verbose)
        self.experiment_name = experiment_name

        self.fileManager = FileManager(self.name, self.work, self.verbose)
        self.num_to_check = self.experiment.experiment_config["number_of_versions_to_check_for_usability"]

        self.generated_mutants_dir = out_dir / self.name / "generated_mutants"
        assert self.generated_mutants_dir.exists(), "Generated mutants directory does not exist"

        self.crashed_buggy_mutants_dir = out_dir / f"{self.name}" / "crashed_buggy_mutants"
        self.crashed_buggy_mutants_dir.mkdir(exist_ok=True, parents=True)
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()
        
        # THIS IS REMOVED WHILE CHANGING FROM FILE TO DB
        self.redoing = False
        """
        self.versions_list = get_dirs_in_dir(self.initial_selected_dir)
        if len(self.versions_list) != 0:
            self.redoing = True
        else:
            self.redoing = False
        if self.redoing == False:
            # 2. Select initial buggy versions at random
            self.select_initial_buggy_versions()

            # 3. Get versions to test
            self.versions_list = get_dirs_in_dir(self.initial_selected_dir)
        """

        # 1. Select initial buggy versions at random
        # connect to db
        self.connect_to_db()
        self.select_initial_buggy_versions()
        self.versions_list = self.get_works(self.generated_mutants_dir, self.experiment_name, "AND initial IS TRUE AND usable IS NULL")

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
        for machine_core, work_infos in self.versions_assignments.items():
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_remote,
                args=(machine, core, homedir, work_infos)
            )
            jobs.append(job)
            job.start()
            time.sleep(0.5) # to avoid ssh connection error

        for job in jobs:
            job.join()
        
        print(f">> Finished testing all versions now retrieving usable versions")
        self.fileManager.collect_data_remote("crashed_buggy_mutants", self.crashed_buggy_mutants_dir, self.versions_assignments)
    
    def test_single_machine_core_remote(self, machine, core, homedir, work_infos):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for version, code_path in work_infos:
            last_cnt += 1
            version_name = version

            optional_flag = ""
            if need_configure:
                optional_flag = "--need-configure"
                need_configure = False
            if self.verbose:
                optional_flag += " --verbose"
            if last_cnt == len(work_infos):
                optional_flag += " --last-version"

            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_usability_check.py --subject {subject_name} --experiment-name {self.experiment_name} --machine {machine_name} --core {core_name} --version {version_name} {optional_flag}"
            ]
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {version_name} +++++\n")
                f.write("+++++ STDOUT +++++\n")
                f.write(res.stdout.decode())
                f.write("\n+++++ STDERR +++++\n")
                f.write(res.stderr.decode())
    
    def test_versions_local(self):
        jobs = []
        for machine_core, work_infos in self.versions_assignments.items():
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_local,
                args=(machine, core, homedir, work_infos)
            )
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()

    def test_single_machine_core_local(self, machine, core, homedir, work_infos):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for version, code_path in work_infos:
            last_cnt += 1
            version_name = version
            
            cmd = [
                "python3", "test_version_usability_check.py",
                "--subject", subject_name, "--experiment-name", self.experiment_name,
                "--machine", machine_name, "--core", core_name, "--version", version_name
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if self.verbose:
                cmd.append("--verbose")
            if last_cnt == len(work_infos):
                cmd.append("--last-version")
            
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=src_dir)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {version_name} +++++\n")
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
            self.prepare_for_local(self.fileManager, self.versions_assignments)
    
    def prepare_for_remote(self):
        self.fileManager.make_assigned_works_dir_remote(self.experiment.machineCores_list, self.stage_name)

        if self.redoing == False:
            self.fileManager.send_works_remote(self.versions_assignments, self.stage_name)
        
        self.fileManager.send_repo_remote(self.subject_repo, self.experiment.machineCores_list)

        self.fileManager.send_configurations_remote(self.experiment.machineCores_dict)
        self.fileManager.send_src_remote(self.experiment.machineCores_dict)
        self.fileManager.send_tools_remote(self.tools_dir, self.experiment.machineCores_dict)
        self.fileManager.send_experiment_configurations_remote(self.experiment.machineCores_dict)
    

    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++ Selecting N amount of versions to test for usability ++++++
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def select_initial_buggy_versions(self):
        # Update by adding a initial column to bug_info table
        if not self.db.column_exists("bug_info", "initial"):
            self.db.add_column("bug_info", "initial BOOLEAN DEFAULT NULL")
        if not self.db.column_exists("bug_info", "usable"):
            self.db.add_column("bug_info", "usable BOOLEAN DEFAULT NULL")

        # write real world buggy versions to bug_info table in db
        # and copy the source file to initial_selected_buggy_versions directory
        if self.real_world_buggy_versions_status:
            self.include_real_world_buggy_versions()

        # Select buggy mutants at random
        bug_idx_list = self.db.read(
            "bug_info",
            columns="bug_idx",
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
            },
            special="AND initial IS NULL AND usable IS NULL"
        )
        bug_idx_list = [row[0] for row in bug_idx_list]

        # Select N amount of buggy mutants to check for usability
        if len(bug_idx_list) > self.num_to_check:
            bug_idx_list = random.sample(bug_idx_list, self.num_to_check)
        print(f"Selected {len(bug_idx_list)} buggy mutants to check for usability at random")

        for bug_idx in bug_idx_list:
            # 1. Update bug_info table in db
            self.db.update(
                "bug_info",
                set_values={"initial": True},
                conditions={"bug_idx": bug_idx}
            )


    def include_real_world_buggy_versions(self):
        # 1. get real world buggy versions directory
        real_world_buggy_versions_dir = self.work / "real_world_buggy_versions"
        
        for buggy_version in real_world_buggy_versions_dir.iterdir():
            # check if the version is already in the db
            exists = self.db.value_exists(
                "bug_info",
                conditions={
                    "subject": self.name,
                    "experiment_name": self.experiment_name,
                    "version": buggy_version.name,
                    "type": "real_world",
                    "initial": True
                }
            )
            if exists:
                continue

            if not buggy_version.is_dir():
                continue

            # 3. write bug_info to bug_info table in db
            bug_info_csv = buggy_version / "bug_info.csv"
            with open(bug_info_csv, "r") as f:
                lines = f.readlines()
                info = lines[1].strip().split(",")
                target_code_file = info[0]
                buggy_code_file = info[1]
                buggy_lineno = int(info[2])

                target_code_file = "/".join(target_code_file.split("/")[1:])
                target_code_file = f"{self.name}/{target_code_file}"

                self.db.insert(
                    "bug_info",
                    "subject, experiment_name, version, type, target_code_file, buggy_code_file, pre_start_line, initial",
                    f"'{self.name}', '{self.experiment_name}', '{buggy_version.name}', 'real_world', '{target_code_file}', '{buggy_code_file}', {buggy_lineno}, TRUE"
                )
            
            bug_idx = self.get_bug_idx(self.name, self.experiment_name, buggy_version.name)
            
            # 4. write test case info to tc_info table in db
            self.db.delete("tc_info", conditions={"bug_idx": bug_idx})

            failing_tcs_txt = buggy_version / "testsuite_info/failing_tcs.txt"
            idx = 0
            with open(failing_tcs_txt, "r") as f:
                lines = f.readlines()
                for line in lines:
                    tc_name = line.strip()
                    tc_result = "fail"
                    tc_ret_code = 1
                    self.db.insert(
                        "tc_info",
                        "bug_idx, tc_idx, tc_name, tc_result, tc_ret_code",
                        f"{bug_idx}, '{idx}', '{tc_name}', '{tc_result}', {tc_ret_code}"
                    )
                    idx += 1
            passing_tcs_txt = buggy_version / "testsuite_info/passing_tcs.txt"
            with open(passing_tcs_txt, "r") as f:
                lines = f.readlines()
                for line in lines:
                    tc_name = line.strip()
                    tc_result = "pass"
                    tc_ret_code = 0
                    self.db.insert(
                        "tc_info",
                        "bug_idx, tc_idx, tc_name, tc_result, tc_ret_code",
                        f"{bug_idx}, {idx}, '{tc_name}', '{tc_result}', {tc_ret_code}"
                    )
                    idx += 1

            self.num_to_check -= 1
