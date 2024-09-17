import time
import multiprocessing
import subprocess as sp
import concurrent.futures

from lib.utils import *
from lib.subject_base import Subject
from lib.file_manager import FileManager

class BuggyMutantCollection(Subject):
    def __init__(self, subject_name, verbose=False):
        super().__init__(subject_name, "stage01", verbose)
        self.mutants_dir = out_dir / self.name / f"generated_mutants"
        self.mutants_dir.mkdir(exist_ok=True)

        self.buggy_mutants_dir = out_dir / self.name / "buggy_mutants"
        self.buggy_mutants_dir.mkdir(exist_ok=True)

        self.crashed_buggy_mutants_dir = out_dir / f"{self.name}" / "crashed_buggy_mutants"
        self.crashed_buggy_mutants_dir.mkdir(exist_ok=True, parents=True)

        self.fileManager = FileManager(self.name, self.work, self.verbose)

    
    def run(self):
        # 1. Read configurations and initialize working directory: self.work
        self.initialize_working_directory()
        
        # 2. Configure subject
        self.configure_no_cov()
        
        # 3. Build subject
        self.build(piping=False)
        
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
            # 4. Generate mutants
            # self.mutants_dir format: path to 'generated_mutants' directory
            # self.targetfile_and_mutantdir format: (target_file, its mutants_dir)
            self.generate_mutants()
        self.clean_build()

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

        # 2024-09-14 commented out to randomize build order for cores in machines
        # for machine_core, mutants in self.mutant_assignments.items():
        #     machine, core, homedir = machine_core.split("::")
        #     job = multiprocessing.Process(
        #         target=self.test_single_machine_core_remote,
        #         args=(machine, core, homedir, mutants)
        #     )
        #     jobs.append(job)
        #     job.start()
        #     sleep_cnt += 1
        #     if sleep_cnt%5==0:
        #         time.sleep(10)
        #     # time.sleep(0.5) # to avoid ssh connection error
        
        for job in jobs:
            job.join()
    
        print(f">> Finished testing mutants now retrieving buggy mutants...")
        self.fileManager.collect_data_remote("buggy_mutants", self.buggy_mutants_dir, self.mutant_assignments)
        self.fileManager.collect_data_remote("crashed_buggy_mutants", self.crashed_buggy_mutants_dir, self.mutant_assignments)
        
    def test_single_machine_core_remote(self, machine, core, homedir, mutants):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True

        for target_file, mutant_path in mutants:
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
            
            cmd = [
                "ssh", f"{machine_name}",
                f"cd {homedir}/FL-dataset-generation-{subject_name}/src && python3 test_mutant_buggy_collection.py --subject {subject_name} --machine {machine_name} --core {core_name} --mutant-path {mutant_input} --target-file-path {target_file_path} {optional_flag}"
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

        for target_file, mutant_path in mutants:
            # mutant_path : is a Path object
            # mutant is last two part of the path libxml2-HTMLparser.c/HTMLparser.MUT730.c
            # target_file : libxml2/HTMLparser.c
            mutant_input = "/".join(mutant_path.parts[-2:])
            target_file_path = target_file

            cmd = [
                "python3", "test_mutant_buggy_collection.py",
                "--subject", subject_name, "--machine", machine_name, "--core", core_name,
                "--mutant-path", mutant_input, "--target-file-path", target_file_path,
            ]
            if need_configure:
                cmd.append("--need-configure")
                need_configure = False
            if self.verbose:
                cmd.append("--verbose")
            
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
        if self.experiment.experiment_config["use_distributed_machines"]:
            self.prepare_for_remote()
        else:
            self.prepare_for_local()


    # +++++++++++++++++++++++++++++
    # ++++++ Preparing stage ++++++
    # +++++++++++++++++++++++++++++
    def prepare_for_remote(self):
        self.fileManager.make_assigned_works_remote_stage01(self.mutant_assignments)
        if self.redoing == False:
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

        # jobs = [] # 2024-09-14 commented out to limit max process to 5
        # for target_file, mutant_dir in self.targetfile_and_mutantdir:
        #     job = multiprocessing.Process(
        #         target=self.generate_mutants_for_single_file,
        #         args=(target_file, mutant_dir)
        #     )
        #     jobs.append(job)
        #     job.start()
        
        # for job in jobs:
        #     job.join()
        
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

        cmd = [
            self.musicup_exec,
            str(target_file),
            '-o', str(mutant_dir),
            # '-ll', '1',
            # '-l', '2',
            '-ll', '1', # limit on line
            '-l', '20', # limit on mutant
            '-d', unused_ops,
            '-p', str(self.compile_command_file)
        ]
        mutant_list = get_files_in_dir(mutant_dir)
        if len(mutant_list) == 0:
            print_command(cmd, self.verbose)
            sp.check_call(cmd, stderr=sp.PIPE, stdout=sp.PIPE)
            sp.check_call(cmd)
        else:
            print(f"{mutant_dir.name} already exists mutants")

    
    def initalize_mutants_dir(self):
        # list: target_file, its mutants_dir
        target_files_with_mutants = []
        for target_file in self.config['target_files']:
            target_file_path = self.work / target_file
            assert target_file_path.exists(), f'{target_file_path} does not exist'

            target_file_name = target_file.replace('/', '-')
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
            target_file = target_mutants_dir.name.replace('-', '/')
            # TEMPORARY
            # if "HTMLparser.c" not in target_file:
            #     continue

            target_mutants = list(target_mutants_dir.glob(subject_lang))
            for mutant in target_mutants:
                mutants_list.append((target_file, mutant))

                # TEMPORARY
                if len(mutants_list) >= 275:
                    break

            # TEMPORARY
            if len(mutants_list) >= 275:
                break
        
        return mutants_list

    def print_number_of_mutants(self):
        print(f">> Generated {len(self.mutants_list)} mutants")

    def print_mutant_assignments(self):
        print(f">> Assigned {len(self.mutants_list)} mutants to {len(self.mutant_assignments)} cores")
        for machine_core, mutants in self.mutant_assignments.items():
            print(f'>> {machine_core} has {len(mutants)} mutants')

    # ++++++++++++++++++++++++++++++++++++++++ # 2024-08-09 save-crashed-buggy-mutants
    # ++++++ Save Crashed Buggy Mutants ++++++
    # ++++++++++++++++++++++++++++++++++++++++
    def save_crashed_buggy_mutants(self):
        self.subject_out_dir = out_dir / self.name
        self.crashed_buggy_mutants_dir = self.subject_out_dir / "crashed_buggy_mutants"
        assert self.crashed_buggy_mutants_dir.exists(), f"{self.crashed_buggy_mutants_dir.name} doesn't exists"

        # self.saved_crashed_buggy_mutants_dir = self.subject_out_dir / "saved_crashed_buggy_mutants"
        # self.saved_crashed_buggy_mutants_dir.mkdir(exist_ok=True, parents=True) # 2024-08-09 save-crashed-buggy-mutants

        self.source2mutDir_dict = self.get_source2smutDir_dict()

        self.crashed_mutant_info = self.get_crash_mutant_info(self.crashed_buggy_mutants_dir)
        self.mbfl_source2lineno = self.get_mbfl_extracted_mutant_info(self.subject_out_dir / "mbfl_features")
        
        # This is how the dictionary looks like
        # {
        #     "source_name": source_name, # ns_app.c
        #     "taget_code_file": target_code_file, # NSFW_c_frw/NSFW/src/frw/ns_app.c
        #     "mut_dir_name": mut_dir_name, # NSFW_c_frw-NSFW-src-frw-ns_app.c
        #     "mutant_dir_Path": mut_info["mut_dir_Path"],
        #     "mutant_file_Path": mut_info["mut_file_Path"],
        #     "mutant_db_csv_Path": mut_info["db_csv_Path"],
        #     "mutant_lineno": mut_info["lineno"],
        # }
        self.notUsed_crashed_mutant_info = self.get_notUsed_crashed_mutant_info(self.crashed_mutant_info, self.mbfl_source2lineno)

        print(f"len of origin crashed: {len(self.crashed_mutant_info)}")
        print(f"len of notUsed crashed: {len(self.notUsed_crashed_mutant_info)}")

        # 1. Read configurations and initialize working directory: self.work
        # self.initialize_working_directory()

        # 5. Get mutants: self.mutants_list
        # self.mutant_list format: [(target_file, mutant)]
        self.mutants_list = [(self.notUsed_crashed_mutant_info[mutant]["taget_code_file"], self.notUsed_crashed_mutant_info[mutant]["mutant_file_Path"]) for mutant in self.notUsed_crashed_mutant_info]
        print(f"len b4 assignment: {len(self.mutants_list)}")
        # self.print_number_of_mutants()

        # 6. Assign mutants to cores
        # mutant_assignments format: {machine_core: [(target_file, mutant)]}
        self.mutant_assignments = self.assign_works_to_machines(self.mutants_list)
        self.print_mutant_assignments()

        # # 7. Prepare for mutation testing
        # self.prepare_for_mutation_testing()

        # # 8. Test mutants
        # self.test_mutants()
    
    def get_crash_mutant_info(self, crash_dir):
        crashed_info = {}
        for csv_file in crash_dir.iterdir():
            info = csv_file.name.split("-")
            mutant_name = info[0] # info 1
            error_type = info[1]
            step = info[2]
            
            splitted_name = mutant_name.split(".")
            source_name = splitted_name[0] + "." + splitted_name[-1] # info 2

            # source_file_path = self.get_source_file_path(mutant_name, source_name)
            assert source_name in self.source2mutDir_dict, f"{source_name} not in source2mutDir_dict"
            target_code_file = self.source2mutDir_dict[source_name]["target_code_file"] # info 3
            mut_dir_name = self.source2mutDir_dict[source_name]["mut_dir_name"] # info 4

            mut_info = self.get_mut_info(mut_dir_name, mutant_name, source_name) # info 5

            if error_type == "crash":
                assert mutant_name not in crashed_info, f"{mutant_name} already in crashed_info dict"
                crashed_info[mutant_name] = {
                    "source_name": source_name, # ns_app.c
                    "taget_code_file": target_code_file, # NSFW_c_frw/NSFW/src/frw/ns_app.c
                    "mut_dir_name": mut_dir_name, # NSFW_c_frw-NSFW-src-frw-ns_app.c
                    "mutant_dir_Path": mut_info["mut_dir_Path"],
                    "mutant_file_Path": mut_info["mut_file_Path"],
                    "mutant_db_csv_Path": mut_info["db_csv_Path"],
                    "mutant_lineno": mut_info["lineno"],
                }
        return crashed_info
    
    def get_mbfl_extracted_mutant_info(self, mbfl_dir):
        source2lineno = {}
        for mbfl_mut_dir in mbfl_dir.iterdir():
            mutant_name = mbfl_mut_dir.name
            splitted_name = mutant_name.split(".")
            source_name = splitted_name[0] + "." + splitted_name[-1]

            mut_dir_name = self.source2mutDir_dict[source_name]["mut_dir_name"]
            mut_info = self.get_mut_info(mut_dir_name, mutant_name, source_name)

            lineno = mut_info["lineno"]
            if source_name not in source2lineno:
                source2lineno[source_name] = []
            assert lineno not in source2lineno[source_name], f"{lineno} coexists..."

            source2lineno[source_name].append(lineno)
            
        return source2lineno
    
    def get_notUsed_crashed_mutant_info(self, crashed_mutants, mbfl_source2lineno):
        notUsed = {}
        for crashed in crashed_mutants.keys():
            crashed_source_name = crashed_mutants[crashed]["source_name"]
            crashed_lineno = crashed_mutants[crashed]["mutant_lineno"]

            # this still allows duplice bug within a line from crashed
            if crashed_source_name not in mbfl_source2lineno:
                mbfl_source2lineno[crashed_source_name] = []

            if crashed_lineno not in mbfl_source2lineno[crashed_source_name]:
                assert crashed not in notUsed, f"{crashed} weirdly is already in notUsed"
                notUsed[crashed] = crashed_mutants[crashed]
                # mbfl_source2lineno[crashed_source_name].append(crashed_lineno) # this comment dis-allows duplicate bug within a line from crashed
        return notUsed

            
    def get_mut_info(self, mut_dir_name, mutant_name, source_name):
        mut_dir = self.mutants_dir / mut_dir_name
        assert mut_dir.exists(), f"{mut_dir} doesn't exists"

        mut_file = mut_dir / mutant_name
        assert mut_file.exists(), f"{mut_file} doesn't exists"

        filename = source_name.split(".")[0]
        db_csv = mut_dir / f"{filename}_mut_db.csv"
        assert db_csv.exists(), f"{db_csv} doesn't exists"

        lineno = self.get_lineno_of_mut(mutant_name, db_csv)
        assert lineno != None, f"Lineno of {mutant_name} is not found in {db_csv}"

        info = {
            "mut_dir_Path": mut_dir,
            "mut_file_Path": mut_file,
            "db_csv_Path": db_csv,
            "lineno": lineno
        }

        return info
    
    def get_lineno_of_mut(self, mut_name, db_csv):
        with open(db_csv, "r") as fp:
            lines = fp.readlines()
            for line in lines[2:]:
                info = line.strip().split(",")
                csv_mut_name = info[0]
                csv_op = info[1]
                csv_lineno = int(info[2])

                if csv_mut_name == mut_name:
                    return csv_lineno
        return None

    
    def get_source2smutDir_dict(self,):
        return_dict = {}
        for mut_dir in self.mutants_dir.iterdir():
            dirname = mut_dir.name
            source_file_name = dirname.split("-")[-1]
            target_code_file = dirname.replace("-","/")
            mut_dir_name = dirname

            return_dict[source_file_name] = {
                "target_code_file": target_code_file,
                "mut_dir_name": dirname
            }
        return return_dict
