import time
import multiprocessing
import subprocess as sp
import random
import shutil

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class MBFLExtraction(Subject):
    def __init__(
            self, subject_name, experiment_name,
            target_set_name, trial,
            verbose=False, past_trials=None, exclude_init_lines=False, # 2024-08-13 exclude lines executed on initialization
            parallel_cnt=0, dont_terminate_leftovers=False, # 2024-08-13 implement parallel mode
            remain_one_bug_per_line_flag=False # 2024-08-16 implement flag for remaining one bug per line
            ):
        self.experiment_name = experiment_name
        self.trial = trial
        self.past_trials = past_trials
        self.stage_name = f"stage05-{trial}"
        self.generated_mutants_dirname = f"generated_mutants"
        self.exclude_init_lines = exclude_init_lines
        self.parallel_cnt = parallel_cnt
        self.dont_terminate_leftovers = dont_terminate_leftovers
        self.remain_one_bug_per_line_flag = remain_one_bug_per_line_flag
        super().__init__(subject_name, self.stage_name, verbose) # 2024-08-07 add-mbfl

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

        # 3. filter versions
        if self.remain_one_bug_per_line_flag == True: # 2024-08-16 implement flag for remaining one bug per line
            self.versions_list = self.remain_one_bug_per_line()

        print(f">> MBFL extraction on {len(self.versions_list)} of buggy versions <<")

        # 4. Assign versions to machines
        self.versions_assignments = self.assign_works_to_machines(self.versions_list)

        # 5. Prepare for testing versions
        self.prepare_for_testing_versions()

        # 6. Test versions
        self.test_versions()
    
    def init_tables(self,):
        # Add for_sbfl_ranked_mbfl, for_random_mbfl column to line_info table
        if not self.db.column_exists("line_info", "for_sbfl_ranked_mbfl_asc"):
            self.db.add_column("line_info", "for_sbfl_ranked_mbfl_asc BOOLEAN DEFAULT NULL")
        if not self.db.column_exists("line_info", "for_sbfl_ranked_mbfl_desc"):
            self.db.add_column("line_info", "for_sbfl_ranked_mbfl_desc BOOLEAN DEFAULT NULL")
        if not self.db.column_exists("line_info", "for_random_mbfl"):
            self.db.add_column("line_info", "for_random_mbfl BOOLEAN DEFAULT NULL")
        
        if not self.db.table_exists("mutation_info"):
            cols = [
                "bug_idx INT NOT NULL", # -- Foreign key to bug_info(bug_idx)
                "is_for_test BOOLEAN DEFAULT NULL",
                "build_result BOOLEAN DEFAULT NULL",
                "parallel_name TEXT",
                "targetting_file TEXT",
                "mutation_dirname TEXT",
                "mutant_filename TEXT",
                "mutant_idx INT",
                "line_idx INT",
                "mut_op TEXT",
                "f2p INT",
                "p2f INT",
                "f2f INT",
                "p2p INT",
                "p2f_cct INT",
                "p2p_cct INT",
                "build_time_duration FLOAT",
                "tc_execution_time_duration FLOAT",
                "ccts_execution_time_duration FLOAT",
                "FOREIGN KEY (bug_idx) REFERENCES bug_info(bug_idx) ON DELETE CASCADE ON UPDATE CASCADE" # -- Automatically delete tc_info rows when bug_info is deleted, Update changes in bug_info to tc_info
            ]
            col_str = ",".join(cols)
            self.db.create_table(
                "mutation_info",
                columns=col_str
            )
            # Create a composite index on (subject, experiment_name, version)
            self.db.create_index(
                "mutation_info",
                "idx_mutation_info_bug_idx",
                "bug_idx"
            )
        
        # Add mbfl column in bug_info table
        if not self.db.column_exists("bug_info", "selected_for_mbfl"):
            self.db.add_column("bug_info", "selected_for_mbfl BOOLEAN DEFAULT NULL")
        if not self.db.column_exists("bug_info", "mbfl"):
            self.db.add_column("bug_info", "mbfl BOOLEAN DEFAULT NULL")
        if not self.db.column_exists("bug_info", "mbfl_wall_clock_time"):
            self.db.add_column("bug_info", "mbfl_wall_clock_time FLOAT")
    
    def remain_one_bug_per_line(self):
        self.connect_to_db()

        perfile_include_idx = {}
        included_bug_idx = []
        included_versions = []
        past_tested_line_idx = {}

        # shuffle self.versions_list
        random.shuffle(self.versions_list)

        for version in self.versions_list:
            bug_idx = self.get_bug_idx(self.name, self.experiment_name, version.name)
            res = self.db.read("bug_info", columns="buggy_line_idx, buggy_file, mbfl, sbfl", conditions={"bug_idx": bug_idx})
            assert len(res) == 1, f"Error: {len(res)} rows are returned for {version.name}"
            line_idx, buggy_file, mbfl, sbfl = res[0]
            
            if mbfl == True:
                if buggy_file not in past_tested_line_idx:
                    past_tested_line_idx[buggy_file] = []
                if line_idx not in past_tested_line_idx[buggy_file]:
                    past_tested_line_idx[buggy_file].append(line_idx)
                continue
            
            if sbfl == False:
                print(f"SBFL is False for {version.name}")
                continue

            if buggy_file in past_tested_line_idx and line_idx in past_tested_line_idx[buggy_file]:
                continue

            if buggy_file not in perfile_include_idx:
                perfile_include_idx[buggy_file] = []
            
            if line_idx not in perfile_include_idx[buggy_file]:
                perfile_include_idx[buggy_file].append(line_idx)
                included_bug_idx.append(bug_idx)
                included_versions.append(version)
            


        special_str = f"WHERE bug_idx IN ({','.join([str(bug_idx) for bug_idx in included_bug_idx])})"
        self.db.update(
            "bug_info",
            set_values={"selected_for_mbfl": True},
            special=special_str
        )
        
        print(f"Remained versions: {len(included_versions)}")
        print(f"Per file count: {len(perfile_include_idx)}")
        for file, line_idx_list in perfile_include_idx.items():
            print(f"{file}: {len(line_idx_list)}")
        
        self.db.__del__()

        return included_versions

    
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
        sleep_cnt = 0
        for machine, machine_batch_dict in batch_dict.items():
            job = multiprocessing.Process(
                target=self.test_single_machine_remote,
                args=(machine, machine_batch_dict)
            )
            jobs.append(job)
            job.start()
            sleep_cnt += 1
            if sleep_cnt % 5 == 0:
                time.sleep(35)

        for job in jobs:
            job.join()
        
        print(f">> Finished testing all versions now retrieving versions with its mbfl data")
        # self.fileManager.collect_data_remote("mbfl_features", self.mbfl_features_dir, self.versions_assignments)
    
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
                        print(f"{batch_id}-{machine} - {len(finished_jobs)} finished jobs with {len(jobs)} leftover, threshold: {threshold}")
                    
                    if entered_termination_phase and time.time() - start_term_time > 1800 and self.past_trials == None and self.dont_terminate_leftovers == False: # 2024-08-07 add-mbfl
                        print(f">> TERMINATING REMAINING JOBS for {batch_id} of {machine} <<")
                        for job in jobs:
                            print(f"Terminating job {job.name}")
                            job.terminate()
                            job.join()

                            # copy the original version of subject for terminated jobs
                            machine = job_args[job.name][0]
                            core = job_args[job.name][1]
                            machine_core_dir = self.working_env / machine / core
                            print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
                            sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])

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
        if self.past_trials != None:
            optional_flag += " --past-trials "
            trials_str = " ".join(self.past_trials)
            optional_flag += trials_str
        if self.exclude_init_lines == True: # 2024-08-13 exclude lines executed on initialization
            optional_flag += " --exclude-init-lines"
        if self.parallel_cnt != 0: # 2024-08-13 implement parallel mode
            optional_flag += " --parallel-cnt "
            optional_flag += str(self.parallel_cnt)


        cmd = [
            "ssh", f"{machine_name}",
            f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_mbfl_features.py --subject {subject_name} --experiment-name {self.experiment_name} --machine {machine_name} --core {core_name} --version {version_name} --trial {self.trial} {optional_flag}"
        ] # 2024-08-07 add-mbfl
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

            sleep_cnt = 0
            for machine_core, (machine, core, homedir, version) in machine_core_dict.items():
                job = multiprocessing.Process(
                    target=self.test_single_machine_core_local,
                    args=(machine, core, homedir, version)
                )
                job_args[job.name] = [machine, core, homedir, version]
                jobs.append(job)
                job.start()
                sleep_cnt += 1
                if sleep_cnt % 5 == 0:
                    time.sleep(35)
            
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
                        print(f"{len(finished_jobs)} finished jobs with {len(jobs)} leftover, threshold: {threshold}")
                    
                    if entered_termination_phase and time.time() - start_term_time > 1800 and self.past_trials == None and self.dont_terminate_leftovers == False: # 2024-08-07 add-mbfl
                        print(f">> TERMINATING REMAINING JOBS <<")
                        for job in jobs:
                            print(f"Terminating job {job.name}")
                            job.terminate()
                            job.join()

                            # copy the original version of subject for terminated jobs
                            machine = job_args[job.name][0]
                            core = job_args[job.name][1]
                            machine_core_dir = self.working_env / machine / core
                            print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
                            sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])
                    
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
            "python3", "test_version_mbfl_features.py",
            "--subject", subject_name,
            "--experiment-name", self.experiment_name,
            "--machine", machine_name, "--core", core_name,
            "--trial", self.trial, # 2024-08-07 add-mbfl
            "--version", version_name
        ]

        if self.verbose:
            cmd.append("--verbose")
        if self.past_trials != None:
            cmd.append("--past-trials")
            cmd.extend(self.past_trials)
        if self.exclude_init_lines == True: # 2024-08-13 exclude lines executed on initialization
            cmd.append("--exclude-init-lines")
        if self.parallel_cnt != 0: # 2024-08-13 implement parallel mode
            cmd.append("--parallel-cnt")
            cmd.append(str(self.parallel_cnt))
        
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