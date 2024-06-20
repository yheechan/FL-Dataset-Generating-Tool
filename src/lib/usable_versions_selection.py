import time
import multiprocessing
import subprocess as sp
import random

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class UsableVersionSelection(Subject):
    def __init__(self, subject_name, verbose=False):
        super().__init__(subject_name, "stage02", verbose)
        self.initial_selected_dir = out_dir / self.name / f"initial_selected_buggy_versions"
        self.initial_selected_dir.mkdir(exist_ok=True)

        self.usable_versions_dir = out_dir / self.name / f"usable_buggy_versions"
        self.usable_versions_dir.mkdir(exist_ok=True)

        self.fileManager = FileManager(self.name, self.work, self.verbose)
        self.num_to_check = self.experiment.experiment_config["number_of_versions_to_check_for_usability"]

        self.generated_mutants_dir = out_dir / self.name / "generated_mutants"
        assert self.generated_mutants_dir.exists(), "Generated mutants directory does not exist"
        self.buggy_mutants_dir = out_dir / self.name / "buggy_mutants"
        assert self.buggy_mutants_dir.exists(), "Buggy mutants directory does not exist"
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()
        
        # 2. Select initial buggy versions at random
        self.select_initial_buggy_versions()

        # 3. Get versions to test
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
            if self.verbose:
                optional_flag += " --verbose"

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

        for version in versions:
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
            
            


    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++ Selecting N amount of versions to test for usability ++++++
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def select_initial_buggy_versions(self):
        # Copy real world buggy versions if exists
        if self.real_world_buggy_versions_status:
            self.copy_real_world_buggy_versions()

        # Select buggy mutants at random
        buggy_mutants_list = get_dirs_in_dir(self.buggy_mutants_dir)
        buggy_mutants_list = random.sample(buggy_mutants_list, self.num_to_check)
        print(f"Selected {len(buggy_mutants_list)} buggy mutants to check for usability at random")

        for buggy_mutant in buggy_mutants_list:
            mutant_name = buggy_mutant.name

            # 1. Read bug_info.csv
            target_code_file, mutant_code_file = self.get_mutant_info(buggy_mutant)

            # 2. Get target file mutant directory ex) libxml2/HTMLparser.c, HTMLparser.MUT123.c
            target_file_mutant_dir_name = target_code_file.replace("/", "-")
            target_file_mutant_dir = self.generated_mutants_dir / target_file_mutant_dir_name
            assert target_file_mutant_dir.exists(), "Target file mutant directory does not exist"

            # 3. Get buggy_code_file
            buggy_code_file = target_file_mutant_dir / mutant_code_file
            assert buggy_code_file.exists(), "Buggy code file does not exist"

            # 4. Get buggy_lineno and mut_db_line
            buggy_lineno, mut_db_line = self.get_buggy_lineno(target_file_mutant_dir, mutant_name)

            # 5. Check if buggy_lineno is in the target file
            mutant_dir_dest = self.initial_selected_dir / mutant_name
            print_command(["mkdir", "-p", mutant_dir_dest], self.verbose)
            mutant_dir_dest.mkdir(exist_ok=True)

            # 6. Write bug info
            self.write_bug_info(
                buggy_mutant, buggy_code_file, mutant_dir_dest, target_code_file, mutant_code_file, buggy_lineno, mut_db_line,
            )
    
    def write_bug_info(self, buggy_mutant, buggy_code_file, mutant_dir_dest, target_code_file, mutant_code_file, buggy_lineno, mut_db_line):
        # Write bug_info.csv
        bug_info_csv = mutant_dir_dest / "bug_info.csv"
        with bug_info_csv.open("w") as f:
            f.write("target_code_file,buggy_code_file,buggy_lineno\n")
            f.write(f"{target_code_file},{mutant_code_file},{buggy_lineno}\n")
        
        # Write mutant_info.csv
        mutant_info_csv = mutant_dir_dest / "mutant_info.csv"
        with mutant_info_csv.open("w") as f:
            f.write(",,,Before Mutation,,,,,After Mutation\n")
            f.write("Mutant Filename,Mutation Operator,Start Line#,Start Col#,End Line#,End Col#,Target Token,Start Line#,Start Col#,End Line#,End Col#,Mutated Token,Extra Info\n")
            f.write(mut_db_line)

        # Copy testsuite_info
        testsuite_info_dir = mutant_dir_dest / "testsuite_info"
        print_command(["mkdir", "-p", testsuite_info_dir], self.verbose)
        testsuite_info_dir.mkdir(exist_ok=True)

        failing_tcs_file = buggy_mutant / "failing_tcs.txt"
        assert failing_tcs_file.exists(), "Failing testcases file does not exist"
        print_command(["cp", failing_tcs_file, testsuite_info_dir], self.verbose)
        sp.check_call(["cp", failing_tcs_file, testsuite_info_dir])

        passing_tcs_file = buggy_mutant / "passing_tcs.txt"
        assert passing_tcs_file.exists(), "Passing testcases file does not exist"
        print_command(["cp", passing_tcs_file, testsuite_info_dir], self.verbose)
        sp.check_call(["cp", passing_tcs_file, testsuite_info_dir])

        # Copy buggy code file
        buggy_code_file_dir = mutant_dir_dest / "buggy_code_file"
        print_command(["mkdir", "-p", buggy_code_file_dir], self.verbose)
        buggy_code_file_dir.mkdir(exist_ok=True)
        print_command(["cp", buggy_code_file, buggy_code_file_dir], self.verbose)
        sp.check_call(["cp", buggy_code_file, buggy_code_file_dir])
        

        
    def get_buggy_lineno(self, target_file_mutant_dir, mutant_name):
        filename = mutant_name.split(".")[0]

        mut_db_csv_name = f"{filename}_mut_db.csv"
        mut_db_csv = target_file_mutant_dir / mut_db_csv_name
        assert mut_db_csv.exists(), "Mutant database csv does not exist"

        with mut_db_csv.open() as f:
            lines = f.readlines()
            for line in lines[2:]:
                mut_db_line = line.strip()
                info = mut_db_line.split(",")

                mut_name = info[0]
                if mut_name == mutant_name:
                    buggy_lineno = int(info[2])
                    return buggy_lineno, mut_db_line


    def get_mutant_info(self, buggy_mutant):
        bug_info_csv = buggy_mutant / "bug_info.csv"
        assert bug_info_csv.exists(), "Bug info csv does not exist"

        with bug_info_csv.open() as f:
            lines = f.readlines()
            info = lines[1].strip().split(",")
            target_code_file = info[0]
            mutant_code_file = info[1]

        return target_code_file, mutant_code_file

    def copy_real_world_buggy_versions(self):
        real_world_buggy_versions_dir = self.work / "real_world_buggy_versions"
        
        for buggy_version in real_world_buggy_versions_dir.iterdir():
            if not buggy_version.is_dir():
                continue
            
            # Copy buggy version to out_dir
            sp.check_call(["cp", "-r", buggy_version, self.initial_selected_dir])

            self.num_to_check -= 1
