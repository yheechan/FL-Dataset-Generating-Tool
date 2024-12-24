import time
import multiprocessing
import subprocess as sp

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class SBFLExtraction(Subject):
    def __init__(
            self, subject_name, experiment_name, target_set_name, verbose=False
            ):
        super().__init__(subject_name, "stage04", verbose)

        self.experiment_name = experiment_name

        self.fileManager = FileManager(self.name, self.work, self.verbose)

        self.target_set_dir = out_dir / self.name / target_set_name
        assert self.target_set_dir.exists(), "Origin set directory does not exist"
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()
        self.connect_to_db()
        self.init_tables()
        self.db.__del__()

        # 2. get versions from set_dir
        self.versions_list = get_dirs_in_dir(self.target_set_dir)

        # 4. Assign versions to machines
        self.versions_assignments = self.assign_works_to_machines(self.versions_list)

        # 5. Prepare for testing versions
        self.prepare_for_testing_versions()

        # 6. Test versions
        self.test_versions()
    
    def init_tables(self):
        # Add SBFL data column in line_info table
        new_cols = [
            "ep INT DEFAULT NULL",
            "np INT DEFAULT NULL",
            "ef INT DEFAULT NULL",
            "nf INT DEFAULT NULL",
            "cct_ep INT DEFAULT NULL",
            "cct_np INT DEFAULT NULL"
        ]
        sbfl_list = [
            "GP13 FLOAT4 DEFAULT NULL",
            "Jaccard FLOAT4 DEFAULT NULL",
            "Naish1 FLOAT4 DEFAULT NULL",
            "Naish2 FLOAT4 DEFAULT NULL",
            "Ochiai FLOAT4 DEFAULT NULL",
            "GP13_cct FLOAT4 DEFAULT NULL",
            "Jaccard_cct FLOAT4 DEFAULT NULL",
            "Naish1_cct FLOAT4 DEFAULT NULL",
            "Naish2_cct FLOAT4 DEFAULT NULL",
            "Ochiai_cct FLOAT4 DEFAULT NULL"
        ]
        for col in new_cols + sbfl_list:
            col_name = col.split(" ")[0].lower()
            if not self.db.column_exists("line_info", col_name):
                self.db.add_column("line_info", col)
        
        # Add sbfl column in bug_info table
        if not self.db.column_exists("bug_info", "sbfl"):
            self.db.add_column("bug_info", "sbfl BOOLEAN DEFAULT NULL")

    
    # +++++++++++++++++++++++++++
    # ++++++ Testing stage ++++++
    # +++++++++++++++++++++++++++    
    def test_versions(self):
        if self.experiment.experiment_config["use_distributed_machines"]:
            self.test_versions_remote()
        else:
            self.test_versions_local()
    
    def test_versions_remote(self):
        # Make batch where:
        # a single batch is a group of versions that will be tested on the same machine but different cores
        # ex) batch_dict: {machine1: {"batch_0": {machine1::core1: [machine1, core1, homedir, version1], machine1::core2: [machine1, core2, homedir, version2], ...}}, machine2: {"batch_0": {machine2::core1: [machine2, core1, homedir, version1], machine2::core2: [machine2, core2, homedir, version2], ...}}, ...}
        batch_dict = {}
        for machine_core, versions in self.versions_assignments.items():
            machine, core, homedir = machine_core.split("::")
            if machine not in batch_dict:
                batch_dict[machine] = {}

            idx = 0
            for version in versions:
                batch_id = f"batch_{idx}"
                if batch_id not in batch_dict[machine]:
                    batch_dict[machine][batch_id] = {}
                assert machine_core not in batch_dict[machine][batch_id], f"Machine core {machine_core} already exists in batch {batch_id}"
                batch_dict[machine][batch_id][machine_core] = [machine, core, homedir, version]
                idx += 1
        
        jobs = []
        for machine, machine_batch_dict in batch_dict.items():
            job = multiprocessing.Process(
                target=self.test_single_machine_remote,
                args=(machine, machine_batch_dict)
            )
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()
        
        print(f">> Finished testing all versions now retrieving versions with its sbfl data")
    
    def test_single_machine_remote(self, machine, machine_batch_dict):
        for batch_id, machine_core_dict in machine_batch_dict.items():
            batch_size = len(machine_core_dict)
            print(f"Batch ID: {batch_id}")
            print(f"Batch size: {batch_size}")

            job_args = {}
            jobs = []
            for machine_core, (machine, core, homedir, version) in machine_core_dict.items():
                job = multiprocessing.Process(
                    target=self.test_single_machine_core_remote,
                    args=(machine, core, homedir, version)
                )
                job_args[job.name] = [machine, core, homedir, version]
                jobs.append(job)
                job.start()
                time.sleep(0.5) # to avoid ssh connection error
            
            threshold = len(jobs)*0.8
            finished_jobs = []
            terminated_jobs = []
            entered_termination_phase = False
            start_term_time = 0
            while len(jobs) > 0:
                for job in jobs:
                    # if finished jobs is more than 80% of the total jobs
                    # and the remaining jobs don't finish within 10 minutes after the "finished jobs > threshold" condition
                    # then terminate the remaining jobs
                    if len(finished_jobs) > threshold and not entered_termination_phase:
                        entered_termination_phase = True
                        start_term_time = time.time()
                        print(f">> ENTERING TERMINATION PHASE for {batch_id} of {machine} <<")
                        print(f"{batch_id}-{machine} - {len(finished_jobs)} finished jobs out of {len(jobs)}, threshold: {threshold}")
                    
                    if entered_termination_phase and time.time() - start_term_time > 600:
                        print(f">> TERMINATING REMAINING JOBS for {batch_id} of {machine} <<")
                        for job in jobs:
                            print(f"Terminating job {job.name}")
                            job.terminate()
                            job.join()
                            terminated_jobs.append(job)
                    
                    # Remove the job from the list if it has finished
                    if not job.is_alive():
                        print(f"{batch_id}-{machine} : Job {job.name} has been finished: {job_args[job.name]}")
                        finished_jobs.append(job)
                        jobs.remove(job)
        
            # killall python3 on the machine
            if len(terminated_jobs) > 0:
                cmd = [
                    "ssh", f"{machine}",
                    "killall python3"
                ]
                print(f"Terminating all python3 processes on {machine}")
                print_command(cmd, self.verbose)
                sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    
    def test_single_machine_core_remote(self, machine, core, homedir, version):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        version_name = version.name

        optional_flag = ""
        if self.verbose:
            optional_flag += " --verbose"

        cmd = [
            "ssh", f"{machine_name}",
            f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_sbfl_features.py --subject {subject_name} --experiment-name {self.experiment_name} --machine {machine_name} --core {core_name} --version {version_name} {optional_flag}"
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

        # Make batch where:
        # a single batch is a group of versions that will be tested on the same machine but different cores
        # ex) batch_0: {machine1::core1: [machine1, core1, homedir, version1], machine1::core2: [machine1, core2, homedir, version2], ...}
        batch_dict = {}
        for machine_core, versions in self.versions_assignments.items():
            idx = 0
            machine, core, homedir = machine_core.split("::")
            machine_core = f"{machine}::{core}"
            # print(f"Machine core: {machine_core}")
            for version in versions:
                batch_id = f"batch_{idx}"
                if batch_id not in batch_dict:
                    batch_dict[batch_id] = {}
                assert machine_core not in batch_dict[batch_id], f"Machine core {machine_core} already exists in batch {batch_id}"
                batch_dict[batch_id][machine_core] = [machine, core, homedir, version]
                idx += 1

        jobs = []
        job_args = {}
        for batch_id, machine_core_dict in batch_dict.items():
            batch_size = len(machine_core_dict)
            print(f"Batch ID: {batch_id}")
            print(f"Batch size: {batch_size}")

            for machine_core, (machine, core, homedir, version) in machine_core_dict.items():
                job = multiprocessing.Process(
                    target=self.test_single_machine_core_local,
                    args=(machine, core, homedir, version)
                )
                job_args[job.name] = [machine, core, homedir, version]
                jobs.append(job)
                job.start()
            
            threshold = len(jobs)*0.8
            finished_jobs = []
            entered_termination_phase = False
            start_term_time = 0
            while len(jobs) > 0:
                for job in jobs:
                    # if finished jobs is more than 80% of the total jobs
                    # and the remaining jobs don't finish within 10 minutes after the "finished jobs > threshold" condition
                    # then terminate the remaining jobs
                    if len(finished_jobs) > threshold and not entered_termination_phase:
                        entered_termination_phase = True
                        start_term_time = time.time()
                        print(f">> ENTERING TERMINATION PHASE <<")
                        print(f"{len(finished_jobs)} finished jobs out of {len(jobs)}, threshold: {threshold}")
                    
                    if entered_termination_phase and time.time() - start_term_time > 600:
                        print(f">> TERMINATING REMAINING JOBS <<")
                        for job in jobs:
                            print(f"Terminating job {job.name}")
                            job.terminate()
                            job.join()
                    
                    # Remove the job from the list if it has finished
                    if not job.is_alive():
                        print(f"Job {job.name} has been finished: {job_args[job.name]}")
                        finished_jobs.append(job)
                        jobs.remove(job)

    def test_single_machine_core_local(self, machine, core, homedir, version):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        version_name = version.name
        
        cmd = [
            "python3", "test_version_sbfl_features.py",
            "--subject", subject_name, "--experiment-name", self.experiment_name,
            "--machine", machine_name, "--core", core_name,
            "--version", version_name
        ]

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
            self.prepare_for_remote(self.fileManager, self.versions_assignments, dir_form=True)
        else:
            self.prepare_for_local(self.fileManager, self.versions_assignments, dir_form=True)
    
    