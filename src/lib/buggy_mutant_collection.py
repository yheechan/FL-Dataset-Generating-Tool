import time
import multiprocessing
import subprocess as sp
import concurrent.futures
import csv

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class BuggyMutantCollection(Subject):
    def __init__(self, subject_name, experiment_name, verbose=False):
        super().__init__(subject_name, "stage01", verbose)
        self.experiment_name = experiment_name

        self.mutants_dir = out_dir / self.name / f"generated_mutants"
        self.mutants_dir.mkdir(exist_ok=True)


        self.crashed_buggy_mutants_dir = out_dir / f"{self.name}" / "crashed_buggy_mutants"
        self.crashed_buggy_mutants_dir.mkdir(exist_ok=True, parents=True)

        self.fileManager = FileManager(self.name, self.work, self.verbose)

    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()
        
        check = []
        self.redoing = False
        self.targetfile_and_mutantdir = self.initalize_mutants_dir()
        for target_file, mutant_dir in self.targetfile_and_mutantdir:
            mutant_list = get_files_in_dir(mutant_dir)
            if len(mutant_list) == 0:
                check.append(0)
                print(f"{target_file} need to generate mutants")
            else:
                check.append(1)
                print(f"{target_file} already exists mutants")
                self.redoing = True
        
        if self.redoing == True:
            for c in check:
                assert c == 1, "something is not as expected"

        if self.redoing == False:
            # 2. Configure subject
            self.configure_no_cov()
            
            # 3. Build subject
            self.build(piping=False)

            # 4. Generate mutants
            # self.mutants_dir format: path to 'generated_mutants' directory
            # self.targetfile_and_mutantdir format: (target_file, its mutants_dir)
            self.generate_mutants()
        self.clean_build()
        # exit() THIS WAS TO CHECK WHETHER MUTATIONS WERE GENERATED CORRECTLY

        # 5. Get mutants: self.mutants_list
        # self.mutant_list format: [(target_file, mutant)]
        self.mutants_list = self.get_mutants_list()
        # self.print_number_of_mutants()

        # 6. Assign mutants to cores
        # mutant_assignments format: {machine_core: [(target_file, mutant)]}
        self.mutant_assignments = self.assign_works_to_machines(self.mutants_list)
        # self.print_mutant_assignments()

        # 7. Prepare for mutation testing
        self.prepare_for_mutation_testing()

        # 8. Test mutants
        self.test_mutants()

        # 9. write mut_op to bug_info table
        self.write_mut_op_to_bug_info_table()
    

    def write_mut_op_to_bug_info_table(self):
        self.connect_to_db()

        # get mutation info
        mut_info = self.get_mutants_info()

        # get bug_info
        bug_info = self.db.read(
            "bug_info",
            columns="bug_idx, version, target_code_file",
            conditions={
                "subject": self.name,
                "experiment_name": self.experiment_name
            }
        )

        # update bug_info
        for bug in bug_info:
            bug_idx, version, target_code_file = bug

            assert target_code_file in mut_info, f"{version} not in mut_info"
            assert version in mut_info[target_code_file], f"{version} not in mut_info[{target_code_file}]"
            mut_data = mut_info[target_code_file][version]
            this_values = {
                "mut_op": mut_data["mut_op"],
                "pre_start_line": mut_data["pre_start_line"],
                "pre_start_col": mut_data["pre_start_col"],
                "pre_end_line": mut_data["pre_end_line"],
                "pre_end_col": mut_data["pre_end_col"],
                "pre_mut": mut_data["pre_mut"],
                "post_start_line": mut_data["post_start_line"],
                "post_start_col": mut_data["post_start_col"],
                "post_end_line": mut_data["post_end_line"],
                "post_end_col": mut_data["post_end_col"],
                "post_mut": mut_data["post_mut"]
            }

            this_conditions = {
                "bug_idx": bug_idx,
                "version": version,
                "target_code_file": target_code_file,
            }

            self.db.update(
                "bug_info",
                set_values=this_values,
                conditions=this_conditions
            )

    def init_tables(self):
        # Create table if not exists: bug_info
        if not self.db.table_exists("bug_info"):
            columns = [
                "bug_idx SERIAL PRIMARY KEY", # -- Surrogate key
                "subject TEXT",
                "experiment_name TEXT",
                "version TEXT",
                "type TEXT",
                "target_code_file TEXT",
                "buggy_code_file TEXT",
                "UNIQUE (subject, experiment_name, version)", # -- Ensure uniqueness
                
                "mut_op TEXT",
                "pre_start_line INT",
                "pre_start_col INT",
                "pre_end_line INT",
                "pre_end_col INT",
                "pre_mut TEXT",
                "post_start_line INT",
                "post_start_col INT",
                "post_end_line INT",
                "post_end_col INT",
                "post_mut TEXT"
            ]
            col_str = ", ".join(columns)
            self.db.create_table("bug_info",col_str)


        # Create table if not exists: tc_info
        if not self.db.table_exists("tc_info"):
            columns = [
                "bug_idx INT NOT NULL", # -- Foreign key to bug_info(bug_idx)
                "tc_name TEXT",
                "tc_result TEXT",
                "tc_ret_code INT",
                "FOREIGN KEY (bug_idx) REFERENCES bug_info(bug_idx) ON DELETE CASCADE ON UPDATE CASCADE" # -- Automatically delete tc_info rows when bug_info is deleted, Update changes in bug_info to tc_info
            ]
            col_str = ", ".join(columns)
            self.db.create_table("tc_info", col_str)
            # Create a composite index on (subject, experiment_name, version)
            self.db.create_index(
                "tc_info",
                "idx_tc_info_bug_idx",
                "bug_idx"
            )
        

    # +++++++++++++++++++++++++++
    # ++++++ Testing stage ++++++
    # +++++++++++++++++++++++++++    
    def test_mutants(self):
        # make a new process (job) for each machine-core

        if self.experiment.experiment_config["use_distributed_machines"]:
            self.test_on_remote()
        else:
            self.test_on_local()
    
    def test_on_remote(self):
        jobs = []
        sleep_cnt = 0
        # make shuffled list of machine_cores
        shuffled_list = list(self.mutant_assignments.keys())
        for machine_core in shuffled_list:
            mutants = self.mutant_assignments[machine_core]
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_remote,
                args=(machine, core, homedir, mutants)
            )
            jobs.append(job)
            job.start()
            sleep_cnt += 1
            if sleep_cnt%5==0:
                time.sleep(10)
            # time.sleep(0.5) # to avoid ssh connection error

        for job in jobs:
            job.join()
    
        print(f">> Finished testing mutants for buggy mutants...")
        self.fileManager.collect_data_remote("crashed_buggy_mutants", self.crashed_buggy_mutants_dir, self.mutant_assignments)
        
    def test_single_machine_core_remote(self, machine, core, homedir, mutants):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for target_file, mutant_path in mutants:
            last_cnt += 1
            # mutant_path : is a Path object
            # mutant is last two part of the path libxml2-HTMLparser.c/HTMLparser.MUT730.c
            # target_file : libxml2/HTMLparser.c
            mutant_input = "/".join(mutant_path.parts[-2:])
            target_file_path = target_file

            optional_flag = ""
            if need_configure:
                optional_flag = "--need-configure"
                need_configure = False
            if self.verbose:
                optional_flag += " --verbose"
            if last_cnt == len(mutants):
                optional_flag += " --last-mutant"
            
            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}/FL-dataset-generation-{subject_name}/src && python3 test_mutant_buggy_collection.py --subject {subject_name} --experiment-name {self.experiment_name} --machine {machine_name} --core {core_name} --mutant-path {mutant_input} --target-file-path {target_file_path} {optional_flag}"
            ]
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, cwd=src_dir)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {mutant_path.name} +++++\n")
                f.write("+++++ STDOUT +++++\n")
                f.write(res.stdout.decode())
                f.write("\n+++++ STDERR +++++\n")
                f.write(res.stderr.decode())

    
    def test_on_local(self):
        jobs = []
        cnt = 0
        sleep_cnt = 0
        for machine_core, mutants in self.mutant_assignments.items():
            machine, core, homedir = machine_core.split("::")
            job = multiprocessing.Process(
                target=self.test_single_machine_core_local,
                args=(machine, core, homedir, mutants)
            )
            jobs.append(job)
            job.start()
            sleep_cnt += 1
            if sleep_cnt%5==0:
                time.sleep(10)
        
        for job in jobs:
            job.join()

    def test_single_machine_core_local(self, machine, core, homedir, mutants):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        last_cnt = 0
        for target_file, mutant_path in mutants:
            last_cnt += 1
            # mutant_path : is a Path object
            # mutant is last two part of the path libxml2-HTMLparser.c/HTMLparser.MUT730.c
            # target_file : libxml2/HTMLparser.c
            mutant_input = "/".join(mutant_path.parts[-2:])
            target_file_path = target_file

            cmd = [
                "python3", "test_mutant_buggy_collection.py",
                "--subject", subject_name, "--experiment-name", self.experiment_name, "--machine", machine_name, "--core", core_name,
                "--mutant-path", mutant_input, "--target-file-path", target_file_path,
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if self.verbose:
                cmd.append("--verbose")
            if last_cnt == len(mutants):
                cmd.append("--last-mutant")
            
            print_command(cmd, self.verbose)
            res = sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, cwd=src_dir)

            # write stdout and stderr to self.log
            log_file = self.log / f"{machine_name}-{core_name}.log"
            with log_file.open("a") as f:
                f.write(f"\n+++++ results for {mutant_path.name} +++++\n")
                f.write("+++++ STDOUT +++++\n")
                f.write(res.stdout.decode())
                f.write("\n+++++ STDERR +++++\n")
                f.write(res.stderr.decode())
    
    def prepare_for_mutation_testing(self):
        self.connect_to_db()
        self.init_tables()
        self.db.__del__()

        if self.experiment.experiment_config["use_distributed_machines"]:
            self.prepare_for_remote()
        else:
            self.prepare_for_local()


    # +++++++++++++++++++++++++++++
    # ++++++ Preparing stage ++++++
    # +++++++++++++++++++++++++++++
    def prepare_for_remote(self):
        self.fileManager.make_assigned_works_remote_stage01(self.mutant_assignments)
        # if self.redoing == False:
        self.fileManager.send_mutants_remote_stage01(self.mutant_assignments)
        
        self.fileManager.send_repo_remote(self.subject_repo, self.experiment.machineCores_list)

        self.fileManager.send_configurations_remote(self.experiment.machineCores_dict)
        self.fileManager.send_src_remote(self.experiment.machineCores_dict)
        self.fileManager.send_tools_remote(self.tools_dir, self.experiment.machineCores_dict)
        self.fileManager.send_experiment_configurations_remote(self.experiment.machineCores_dict)

    # MAYBE I can send this as a class of FileManager?
    def prepare_for_local(self):
        self.working_env = self.fileManager.make_working_env_local()

        for machine_core, mutants in self.mutant_assignments.items():
            machine, core, homedir = machine_core.split("::")
            machine_core_dir = self.working_env / machine / core
            assigned_dir = machine_core_dir / f"{self.stage_name}-assigned_works"

            target_dirs = []
            for target_file, mutant in mutants:
                target_dir = mutant.parent.name
                
                # This part makes directory for each target file mutants
                if target_dir not in target_dirs:
                    target_dirs.append(target_dir)
                    target_dir_path = assigned_dir / target_dir
                    print_command(["mkdir", "-p", target_dir_path], self.verbose)
                    target_dir_path.mkdir(exist_ok=True, parents=True)

                # This part copies mutant to assigned directory
                target_dir_path = assigned_dir / target_dir
                mutant_path = target_dir_path / mutant.name
                if self.redoing == False:
                    if not mutant_path.exists():
                        print_command(["cp", mutant, mutant_path], self.verbose)
                        mutant_path.symlink_to(mutant)

            # This part copies subject repository to the machine-core directory
            print_command(["cp", "-r", self.subject_repo, machine_core_dir], self.verbose)
            sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])


    # ++++++++++++++++++++++++++++++++++++
    # ++++++ Gen mutants and assign ++++++
    # ++++++++++++++++++++++++++++++++++++
    def generate_mutants(self):
        # self.targetfile_and_mutantdir = self.initalize_mutants_dir()

        start_time = time.time()
       
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        # Submit the tasks to the pool, it will ensure that only 5 run concurrently
            futures = [
                executor.submit(self.generate_mutants_for_single_file, target_file, mutant_dir)
                for target_file, mutant_dir in self.targetfile_and_mutantdir
            ]

            # Wait for all submitted tasks to complete
            for future in concurrent.futures.as_completed(futures):
                future.result()  # You can add error handling here if needed
        
        print(f">> Finished generating mutants in {time.time() - start_time} seconds")
    
    def generate_mutants_for_single_file(self, target_file, mutant_dir):
        print(f'>> Generating mutants for {target_file.name}')
        unused_ops = ",".join(not_using_operators_in_buggy_mutant_collection)
        # this is specially done for dxt.cpp (opencv_core) because it has too many constants to mutate
        if target_file.name == "dxt.cpp":
            unused_ops += "," + ",".join(["CGCR", "CLCR", "CGSR", "CLSR"])
        cmd = [
            self.musicup_exec,
            str(target_file),
            '-o', str(mutant_dir),
            # '-ll', '1',
            # '-l', '2',
            '-ll', '1', # limit on line
            '-l', '20', # limit on mutant operator
            '-d', unused_ops,
            '-p', str(self.compile_command_file)
        ]
        mutant_list = get_files_in_dir(mutant_dir)
        if len(mutant_list) == 0:
            print_command(cmd, self.verbose)
            # sp.check_call(cmd, stderr=sp.PIPE, stdout=sp.PIPE)
            sp.check_call(cmd)
        else:
            print(f"{mutant_dir.name} already exists mutants")

    
    def initalize_mutants_dir(self):
        # list: target_file, its mutants_dir
        target_files_with_mutants = []
        for target_file in self.config['target_files']:
            target_file_path = self.work / target_file
            assert target_file_path.exists(), f'{target_file_path} does not exist'

            target_file_name = target_file.replace('/', '#')
            single_file_mutant_dir = self.mutants_dir / f"{target_file_name}"
            single_file_mutant_dir.mkdir(exist_ok=True)

            target_files_with_mutants.append((target_file_path, single_file_mutant_dir))
        
        return target_files_with_mutants

    def get_mutants_list(self):
        subject_lang = None
        if self.config["subject_language"] == "C":
            subject_lang = "*.c"
        elif self.config["subject_language"] == "CPP":
            subject_lang = "*.cpp"
        else:
            raise Exception("Subject language not supported")

        mutants_list = []
        for target_mutants_dir in self.mutants_dir.iterdir():
            target_file = target_mutants_dir.name.replace('#', '/')
            # TEMPORARY
            # if "HTMLparser.c" not in target_file:
            #     continue

            target_mutants = list(target_mutants_dir.glob(subject_lang))
            for mutant in target_mutants:
                mutants_list.append((target_file, mutant))

            #     # TEMPORARY
            #     if len(mutants_list) >= 8:
            #         break

            # # TEMPORARY
            # if len(mutants_list) >= 8:
            #     break
        
        return mutants_list
    
    def get_mutants_info(self):
        mut_info = {}
        for target_mutants_dir in self.mutants_dir.iterdir():
            target_file = target_mutants_dir.name.replace('#', '/')
            target_file_source_filename = ".".join(target_file.split('/')[-1].split(".")[:-1])
            mut_db_file = target_mutants_dir / f"{target_file_source_filename}_mut_db.csv"
            assert mut_db_file.exists(), f"{mut_db_file} doesn't exists"

            if target_file not in mut_info:
                mut_info[target_file] = {}

            with open(mut_db_file, "r") as fp:
                # read with csv
                csv_reader = csv.reader(fp, escapechar='\\', quotechar='"', delimiter=',')
                next(csv_reader)
                next(csv_reader)
                for row in csv_reader:
                    mut_name = row[0]
                    op = row[1]
                    pre_start_line = row[2]
                    pre_start_col = row[3]
                    pre_end_line = row[4]
                    pre_end_col = row[5]
                    pre_mut = row[6]
                    post_start_line = row[7]
                    post_start_col = row[8]
                    post_end_line = row[9]
                    post_end_col = row[10]
                    post_mut = row[11]

                    mut_info[target_file][mut_name] = {
                        "mut_op": op,
                        "pre_start_line": pre_start_line,
                        "pre_start_col": pre_start_col,
                        "pre_end_line": pre_end_line,
                        "pre_end_col": pre_end_col,
                        "pre_mut": pre_mut,
                        "post_start_line": post_start_line,
                        "post_start_col": post_start_col,
                        "post_end_line": post_end_line,
                        "post_end_col": post_end_col,
                        "post_mut": post_mut
                    }
        return mut_info

            

    def print_number_of_mutants(self):
        print(f">> Generated {len(self.mutants_list)} mutants")

    def print_mutant_assignments(self):
        print(f">> Assigned {len(self.mutants_list)} mutants to {len(self.mutant_assignments)} cores")
        for machine_core, mutants in self.mutant_assignments.items():
            print(f'>> {machine_core} has {len(mutants)} mutants')
