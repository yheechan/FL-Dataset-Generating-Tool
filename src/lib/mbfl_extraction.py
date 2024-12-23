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
            self, subject_name, target_set_name, trial,
            verbose=False, past_trials=None, exclude_init_lines=False, # 2024-08-13 exclude lines executed on initialization
            parallel_cnt=0, dont_terminate_leftovers=False, # 2024-08-13 implement parallel mode
            remain_one_bug_per_line_flag=False # 2024-08-16 implement flag for remaining one bug per line
            ):
        self.trial = trial
        self.past_trials = past_trials
        self.stage_name = f"stage04-{trial}"
        self.generated_mutants_dirname = f"generated_mutants"
        self.exclude_init_lines = exclude_init_lines
        self.parallel_cnt = parallel_cnt
        self.dont_terminate_leftovers = dont_terminate_leftovers
        self.remain_one_bug_per_line_flag = remain_one_bug_per_line_flag
        super().__init__(subject_name, self.stage_name, verbose) # 2024-08-07 add-mbfl
        self.mbfl_features_dir = out_dir / self.name / f"mbfl_features"
        self.mbfl_features_dir.mkdir(exist_ok=True)

        self.fileManager = FileManager(self.name, self.work, self.verbose)

        self.target_set_dir = out_dir / self.name / target_set_name
        assert self.target_set_dir.exists(), "Origin set directory does not exist"
    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()

        # 2. get versions from set_dir
        self.versions_list = get_dirs_in_dir(self.target_set_dir)

        # TODO: ~
        # 2024-08-01: only remain 1 bug per line
        # generated_mutants_dir = out_dir / self.name / self.generated_mutants_dirname
        # if generated_mutants_dir.exists(): # I DONT THINK THIS IS NEEDED!
        if self.remain_one_bug_per_line_flag == True: # 2024-08-16 implement flag for remaining one bug per line
            self.versions_list = self.remain_one_bug_per_line()
        
        print(f">> MBFL extraction on {len(self.versions_list)} of buggy versions <<")

        # 4. Assign versions to machines
        self.versions_assignments = self.assign_works_to_machines(self.versions_list)

        # 5. Prepare for testing versions
        self.prepare_for_testing_versions()

        # 6. Test versions
        self.test_versions()
    
    def remain_one_bug_per_line(self): # 2024-08-01
        included = 0
        excluded = 0

        generated_mutants_dir = out_dir / self.name / self.generated_mutants_dirname
        # version name: line number
        new_version_list = []
        new_version_dict = {}

        # check every version
        for version in self.versions_list:
            mutant_name = version.name
            filename = ".".join(mutant_name.split(".")[:-2])
            extension = mutant_name.split(".")[-1]
            file_name = filename + "." + extension

            # retrieve mutant dir for mutant
            target_mutant_dir = None
            for mutant_dir in generated_mutants_dir.iterdir():
                mutant_dir_name = mutant_dir.name.split("-")[-1]
                if file_name == mutant_dir_name:
                    target_mutant_dir = mutant_dir
                    break
            assert target_mutant_dir != None, f"target mutant dir is not found for {file_name}"

            # retrieve mut db csv file for mutant
            db_name = filename + "_mut_db.csv"
            db_csv = target_mutant_dir / db_name
            assert db_csv.exists(), f"{db_csv.name} does not exist for {mutant_name}"

            # retrieve line_no for mutant
            line_no = None
            with open(db_csv, "r") as fp:
                lines = fp.readlines()
                for line in lines[2:]:
                    info = line.strip().split(",")
                    mut_name = info[0]

                    if mutant_name == mut_name:
                        line_no = int(info[2])
            
            assert line_no != None, f"line_no is None for {mutant_name}"

            # remain single bug in single line of target file
            if file_name not in new_version_dict:
                new_version_dict[file_name] = []
            
            if line_no not in new_version_dict[file_name]:
                new_version_dict[file_name].append(line_no)
                new_version_list.append(version)
                included += 1
            else:
                excluded += 1
        
        print(f"# of version remaining versions after leaving only one bug in each line: {included}")
        print(f"# of version excluded versions after leaving only one bug in each line: {excluded}")
        # print(json.dumps(new_version_dict, indent=2))
    
        return new_version_list
    
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
        self.fileManager.collect_data_remote("mbfl_features", self.mbfl_features_dir, self.versions_assignments)
    
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
            f"cd {homedir}FL-dataset-generation-{subject_name}/src && python3 test_version_mbfl_features.py --subject {subject_name} --machine {machine_name} --core {core_name} --version {version_name} --trial {self.trial} {optional_flag}"
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
            "--subject", subject_name, "--machine", machine_name, "--core", core_name,
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
            self.prepare_for_remote(self.fileManager, self.versions_assignments)
        else:
            self.prepare_for_local(self.fileManager, self.versions_assignments)