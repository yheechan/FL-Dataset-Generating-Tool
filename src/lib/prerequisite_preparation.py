import time
import multiprocessing
import subprocess as sp
import random

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class PrerequisitePreparation(Subject):
    def __init__(
            self, subject_name, experiment_name, version_limit, verbose=False
        ):
        super().__init__(subject_name, "stage03", verbose)
        self.experiment_name = experiment_name
        self.version_limit = version_limit

        self.fileManager = FileManager(self.name, self.work, self.verbose)
        self.generated_mutants_dir = out_dir / self.name / "generated_mutants"
        assert self.generated_mutants_dir.exists(), "Generated mutants directory does not exist"

        self.prerequisite_data_dir = out_dir / self.name / f"prerequisite_data"
        self.prerequisite_data_dir.mkdir(exist_ok=True)

        self.allPassisCCTdir = out_dir / f"{self.name}" / "allPassisCCT"
        self.allPassisCCTdir.mkdir(exist_ok=True, parents=True)
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()

        # 2. get versions from db
        self.connect_to_db()
        self.init_tables()
        self.versions_list = self.get_usable_buggy_versions()

        if self.version_limit > 0 and len(self.versions_list) > self.version_limit:
            # shuffle the list of versions
            random.shuffle(self.versions_list)
            self.versions_list = self.versions_list[:self.version_limit]

        # 4. Assign versions to machines
        self.versions_assignments = self.assign_works_to_machines(self.versions_list)

        # 5. Prepare for testing versions
        self.prepare_for_testing_versions()

        # 6. Test versions
        self.test_versions()
    
    def get_usable_buggy_versions(self):
        
        bug_list = self.get_works(
            self.generated_mutants_dir,
            self.experiment_name,
            "AND initial IS TRUE AND usable IS TRUE AND prerequisites IS NULL"
        )
        print(f"Number of buggy versions: {len(bug_list)}")
        return bug_list

    def init_tables(self,):
        if not self.db.column_exists("bug_info", "prerequisites"):
            self.db.add_column("bug_info", "prerequisites BOOLEAN DEFAULT NULL")

        # Create table if not exists: line_info
        if not self.db.table_exists("line_info"):
            columns = [
                "bug_idx INT NOT NULL", # -- Foreign key to bug_info(bug_idx)
                "file TEXT DEFAULT NULL",
                "function TEXT DEFAULT NULL",
                "lineno INT DEFAULT NULL",
                "line_idx INT",
                "is_buggy_line BOOLEAN DEFAULT NULL",
                "FOREIGN KEY (bug_idx) REFERENCES bug_info(bug_idx) ON DELETE CASCADE ON UPDATE CASCADE" # -- Automatically delete tc_info rows when bug_info is deleted, Update changes in bug_info to tc_info
            ]
            col_str = ", ".join(columns)
            self.db.create_table("line_info", col_str)

            # Create a composite index on (subject, experiment_name, version)
            self.db.create_index(
                "line_info",
                "idx_line_info_bug_idx",
                "bug_idx"
            )

        # Make coverage csv file
        if not self.db.column_exists("tc_info", "cov_bit_seq"):
            self.db.add_column("tc_info", "cov_bit_seq TEXT DEFAULT NULL")
        
        # Add buggy_line_key in bug info table
        if not self.db.column_exists("bug_info", "buggy_file"):
            self.db.add_column("bug_info", "buggy_file TEXT DEFAULT NULL")
        if not self.db.column_exists("bug_info", "buggy_function"):
            self.db.add_column("bug_info", "buggy_function TEXT DEFAULT NULL")
        if not self.db.column_exists("bug_info", "buggy_lineno"):
            self.db.add_column("bug_info", "buggy_lineno INT DEFAULT NULL")
        if not self.db.column_exists("bug_info", "buggy_line_idx"):
            self.db.add_column("bug_info", "buggy_line_idx INT DEFAULT NULL")

        # Add summary columns in bug info table
        cov_summary = [
            "num_failing_tcs INT",
            "num_passing_tcs INT",
            "num_ccts INT",
            "num_total_tcs INT",
            "num_lines_executed_by_failing_tcs INT",
            "num_lines_executed_by_passing_tcs INT",
            "num_lines_executed_by_ccts INT",
            "num_total_lines_executed INT",
            "num_total_lines INT",
            "num_funcs_executed_by_failing_tcs INT",
            "num_total_funcs INT",
        ]
        for col in cov_summary:
            col_name = col.split(" ")[0]
            if not self.db.column_exists("bug_info", col_name):
                self.db.add_column("bug_info", col)

    
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
        
        print(f">> Finished testing all versions now retrieving versions with its prerequisite data")
        self.fileManager.collect_data_remote("prerequisite_data", self.prerequisite_data_dir, self.versions_assignments)
        self.fileManager.collect_data_remote("allPassisCCT", self.allPassisCCTdir, self.versions_assignments)
    
    def test_single_machine_core_remote(self, machine, core, homedir, work_infos):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for version_name, code_path in work_infos:
            last_cnt += 1

            optional_flag = ""
            if need_configure:
                optional_flag = "--need-configure"
                need_configure = False
            if last_cnt == len(work_infos):
                optional_flag += " --last-version"
            if self.verbose:
                optional_flag += " --verbose"

            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_prerequisites.py --subject {subject_name} --experiment-name {self.experiment_name} --machine {machine_name} --core {core_name} --version {version_name} {optional_flag}"
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
        for version_name, code_path in work_infos:
            last_cnt += 1
            
            cmd = [
                "python3", "test_version_prerequisites.py",
                "--subject", subject_name, "--experiment-name", self.experiment_name,
                "--machine", machine_name, "--core", core_name,
                "--version", version_name
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if last_cnt == len(work_infos):
                cmd.append("--last-version")
            if self.verbose:
                cmd.append("--verbose")
            
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
            self.prepare_for_remote(self.fileManager, self.versions_assignments)
        else:
            self.prepare_for_local(self.fileManager, self.versions_assignments)
    