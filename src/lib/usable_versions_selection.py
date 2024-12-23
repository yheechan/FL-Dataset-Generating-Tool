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

        self.initial_selected_dir = out_dir / self.name / f"initial_selected_buggy_versions"
        self.initial_selected_dir.mkdir(exist_ok=True)

        self.usable_versions_dir = out_dir / self.name / f"usable_buggy_versions"
        self.usable_versions_dir.mkdir(exist_ok=True)

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
        self.select_initial_buggy_versions()
        self.versions_list = get_dirs_in_dir(self.initial_selected_dir)


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
        
        print(f">> Finished testing all versions now retrieving usable versions")
        self.fileManager.collect_data_remote("usable_buggy_versions", self.usable_versions_dir, self.versions_assignments)
        self.fileManager.collect_data_remote("crashed_buggy_mutants", self.crashed_buggy_mutants_dir, self.versions_assignments)
    
    def test_single_machine_core_remote(self, machine, core, homedir, versions):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for version in versions:
            last_cnt += 1
            version_name = version.name

            optional_flag = ""
            if need_configure:
                optional_flag = "--need-configure"
                need_configure = False
            if self.verbose:
                optional_flag += " --verbose"
            if last_cnt == len(versions):
                optional_flag += " --last-version"

            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_usability_check.py --subject {subject_name} --machine {machine_name} --core {core_name} --version {version_name} {optional_flag}"
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

        last_cnt = 0
        for version in versions:
            last_cnt += 1
            version_name = version.name
            
            cmd = [
                "python3", "test_version_usability_check.py",
                "--subject", subject_name, "--machine", machine_name, "--core", core_name,
                "--version", version_name
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if self.verbose:
                cmd.append("--verbose")
            if last_cnt == len(versions):
                cmd.append("--last-version")
            
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

        if self.redoing == False:
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

            if self.redoing == False:
                for version in versions:
                    print_command(["cp", "-r", version, assigned_dir], self.verbose)
                    sp.check_call(["cp", "-r", version, assigned_dir])
            
            core_repo_dir = machine_core_dir / f"{self.name}"
            if not core_repo_dir.exists():
                print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
                sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])
            
            


    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++ Selecting N amount of versions to test for usability ++++++
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def select_initial_buggy_versions(self):
        # connect to db
        self.connect_to_db()

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
        buggy_mutants_list = self.db.read(
            "bug_info",
            columns="version",
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name,
            },
            special="AND initial IS NULL"
        )
        buggy_mutants_list = [row[0] for row in buggy_mutants_list]

        # Select N amount of buggy mutants to check for usability
        if len(buggy_mutants_list) > self.num_to_check:
            buggy_mutants_list = random.sample(buggy_mutants_list, self.num_to_check)
        print(f"Selected {len(buggy_mutants_list)} buggy mutants to check for usability at random")

        for buggy_mutant in buggy_mutants_list:
            # 1. Update bug_info table in db
            self.db.update(
                "bug_info",
                {"initial": True},
                {
                    "subject": self.name,
                    "experiment_name": self.experiment_name,
                    "version": buggy_mutant,
                }
            )

            # 2. get bug info
            data = self.db.read(
                "bug_info",
                columns="target_code_file, buggy_code_file",
                conditions={
                    "subject": self.name,
                    "experiment_name": self.experiment_name,
                    "version": buggy_mutant
                }
            )
            assert len(data) == 1, "Data does not exist in bug_info table"
            target_code_file, buggy_code_file = data[0]

            # 3. copy buggy_code_file into initial_selected_buggy_versions directory
            buggy_code_file_dir = self.initial_selected_dir / buggy_mutant / "buggy_code_file"
            buggy_code_file_dir.mkdir(exist_ok=True, parents=True)


            # Get target file mutant directory ex) libxml2/HTMLparser.c, HTMLparser.MUT123.c
            target_file_mutant_dir_name = target_code_file.replace("/", "-")
            target_file_mutant_dir = self.generated_mutants_dir / target_file_mutant_dir_name
            assert target_file_mutant_dir.exists(), "Target file mutant directory does not exist"

            # Get buggy_code_file
            buggy_code_file = target_file_mutant_dir / buggy_code_file
            assert buggy_code_file.exists(), "Buggy code file does not exist"

            sp.check_call(["cp", buggy_code_file, buggy_code_file_dir])

            buggy_code_file = buggy_code_file_dir / buggy_code_file.name
            assert buggy_code_file.exists(), "Buggy code file does not exist in initial_selected_buggy_versions directory"

    

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
                bug_dir = self.initial_selected_dir / buggy_version.name
                assert bug_dir.exists(), "Real world buggy version does not exist in initial_selected_buggy_versions directory"
                continue

            if not buggy_version.is_dir():
                continue
            
            # 2. copy buggy_code_file_dir into initial_selected_buggy_versions directory
            init_version_dir = self.initial_selected_dir / buggy_version.name
            init_version_dir.mkdir(exist_ok=True)

            buggy_code_file_dir = buggy_version / "buggy_code_file"
            sp.check_call(["cp", "-r", buggy_code_file_dir, init_version_dir])

            # 3. write bug_info to bug_info table in db
            bug_info_csv = buggy_version / "bug_info.csv"
            with open(bug_info_csv, "r") as f:
                lines = f.readlines()
                info = lines[1].strip().split(",")
                target_code_file = info[0]
                buggy_code_file = info[1]
                buggy_lineno = int(info[2])

                self.db.insert(
                    "bug_info",
                    "subject, experiment_name, version, type, target_code_file, buggy_code_file, pre_start_line, initial",
                    f"'{self.name}', '{self.experiment_name}', '{buggy_version.name}', 'real_world', '{target_code_file}', '{buggy_code_file}', {buggy_lineno}, TRUE"
                )
            
            # 4. write test case info to tc_info table in db
            self.db.delete(
                "tc_info",
                conditions={
                    "subject": self.name,
                    "experiment_name": self.experiment_name,
                    "version": buggy_version.name
                }
            )

            failing_tcs_txt = buggy_version / "testsuite_info/failing_tcs.txt"
            with open(failing_tcs_txt, "r") as f:
                lines = f.readlines()
                for line in lines:
                    tc_name = line.strip()
                    tc_result = "fail"
                    tc_ret_code = 1
                    self.db.insert(
                        "tc_info",
                        "subject, experiment_name, version, tc_name, tc_result, tc_ret_code",
                        f"'{self.name}', '{self.experiment_name}', '{buggy_version.name}', '{tc_name}', '{tc_result}', {tc_ret_code}"
                    )
            passing_tcs_txt = buggy_version / "testsuite_info/passing_tcs.txt"
            with open(passing_tcs_txt, "r") as f:
                lines = f.readlines()
                for line in lines:
                    tc_name = line.strip()
                    tc_result = "pass"
                    tc_ret_code = 0
                    self.db.insert(
                        "tc_info",
                        "subject, experiment_name, version, tc_name, tc_result, tc_ret_code",
                        f"'{self.name}', '{self.experiment_name}', '{buggy_version.name}', '{tc_name}', '{tc_result}', {tc_ret_code}"
                    )

            self.num_to_check -= 1
