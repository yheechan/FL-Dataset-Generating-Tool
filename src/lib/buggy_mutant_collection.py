import time
import multiprocessing
import subprocess as sp

from lib.utils import *
from lib.subject_base import Subject
from lib.mutant_bug_collection import MutantBugCollection

class BuggyMutantCollection(Subject):
    def __init__(self, subject_name):
        super().__init__(subject_name, "stage01")

        self.mutants_dir = self.work / 'generated_mutants'
        self.mutants_dir.mkdir(exist_ok=True)
    
    def run(self):
        # # 1. Read configurations and initialize working directory: self.work
        # self.initialize_working_directory()
        
        # # 2. Configure subject
        # self.configure_no_cov()
        
        # # 3. Build subject
        # self.build()
        
        # # 4. Generate mutants
        # # self.mutants_dir format: path to 'generated_mutants' directory
        # # self.targetfile_and_mutantdir format: (target_file, its mutants_dir)
        # self.generate_mutants()

        # # 5. Get mutants: self.mutants_list
        # # self.mutant_list format: [(target_file, mutant)]
        self.mutants_list = self.get_mutants_list()
        # self.print_number_of_mutants()

        # # 6. Assign mutants to cores
        # # mutant_assignments format: {machine_core: [(target_file, mutant)]}
        self.mutant_assignments = self.assign_mutants_to_cores()
        self.print_mutant_assignments()

        # 7. Prepare for mutation testing
        self.prepare_for_mutation_testing()

        # self.experiment.print_machines()

        # 8. Test mutants
        self.test_mutants()
    
    def test_mutants(self):
        # make a new process (job) for each machine-core
        jobs = []

        if self.experiment.experiment_config["use_distributed_machines"]:
            pass
        else:
            for machine_core, mutants in self.mutant_assignments.items():
                machine, core, homedir = machine_core.split("::")
                job = multiprocessing.Process(
                    target=self.test_single_machine_core,
                    args=(machine, core, homedir, mutants)
                )
                jobs.append(job)
                job.start()
            
            for job in jobs:
                job.join()  


    def test_single_machine_core(self, machine, core, homedir, mutants):
        print(f'>> Testing mutants on {machine}::{core}')
        for target_file, mutant in mutants:
            # /home/yangheechan/mbfl-dataset-gen/LIGNex1_FL_dataset_LIBXML2_copy/work/libxml2-stage01/generated_mutants/libxml2-parser.c/parser.MUT6266.c
            # get last two from the path
            mutant = "/".join(mutant.parts[-2:])
            print(f'>> Testing mutant {mutant} on {target_file}')
            mutant_object = MutantBugCollection()
            # self.test_single_mutant(machine_core, target_file, mutant)
    
    def prepare_for_mutation_testing(self):
        if self.experiment.experiment_config["use_distributed_machines"]:
            pass
        else:
            self.prepare_for_local()


    def prepare_for_local(self):
        working_env = self.work / "workers-collecting_mutants"
        working_env.mkdir(exist_ok=True)

        for machine_core, mutants in self.mutant_assignments.items():
            machine, core, homedir = machine_core.split("::")
            machine_core_dir = working_env / f"{machine}/{core}"
            assigned_dir = machine_core_dir / "assigned_works"

            target_dirs = []
            for target_file, mutant in mutants:
                target_dir = mutant.parent.name
                
                # This part makes directory for each target file mutants
                if target_dir not in target_dirs:
                    target_dirs.append(target_dir)
                    target_dir_path = assigned_dir / target_dir
                    target_dir_path.mkdir(exist_ok=True, parents=True)

                # This part copies mutant to assigned directory
                target_dir_path = assigned_dir / target_dir
                mutant_path = target_dir_path / mutant.name
                if not mutant_path.exists():
                    mutant_path.symlink_to(mutant)
            
            # This part makes directory for buggy mutants to be collected
            buggy_mutant_dir = machine_core_dir / 'buggy_mutants'
            buggy_mutant_dir.mkdir(exist_ok=True, parents=True)

            # This part copies subject repository to the machine-core directory
            sp.check_call(["cp", "-r", self.subject_repo, machine_core_dir])


    def assign_mutants_to_cores(self):
        mutant_assignments = {}
        for idx, (target_file, mutant) in enumerate(self.mutants_list):
            machine_core = self.experiment.machines[idx % len(self.experiment.machines)]

            machine_core_str = "::".join(machine_core)

            if machine_core_str not in mutant_assignments:
                mutant_assignments[machine_core_str] = []
            
            mutant_assignments[machine_core_str].append((target_file, mutant))
        
        return mutant_assignments
    
    def generate_mutants(self):
        self.targetfile_and_mutantdir = self.initalize_mutants_dir()

        start_time = time.time()

        jobs = []
        for target_file, mutant_dir in self.targetfile_and_mutantdir:
            job = multiprocessing.Process(
                target=self.generate_mutants_for_single_file,
                args=(target_file, mutant_dir)
            )
            jobs.append(job)
            job.start()
        
        for job in jobs:
            job.join()
        
        print(f">> Finished generating mutants in {time.time() - start_time} seconds")
    
    def generate_mutants_for_single_file(self, target_file, mutant_dir):
        print(f'>> Generating mutants for {target_file.name}')
        unused_ops = ",".join(not_using_operators_in_buggy_mutant_collection)

        cmd = [
            self.musicup_exec,
            str(target_file),
            '-o', str(mutant_dir),
            '-ll', '1',
            '-l', '2',
            '-d', unused_ops,
            '-p', str(self.compile_command_file)
        ]

        sp.check_call(cmd, stderr=sp.PIPE, stdout=sp.PIPE)

    
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

            target_mutants = list(target_mutants_dir.glob(subject_lang))
            for mutant in target_mutants:
                mutants_list.append((target_file, mutant))

                # TEMPORARY
                if len(mutants_list) >= 30:
                    break

            # TEMPORARY
            if len(mutants_list) >= 30:
                break
        
        return mutants_list


    def print_number_of_mutants(self):
        print(f">> Generated {len(self.mutants_list)} mutants")

    def print_mutant_assignments(self):
        print(f">> Assigned {len(self.mutants_list)} mutants to {len(self.mutant_assignments)} cores")
        for machine_core, mutants in self.mutant_assignments.items():
            print(f'>> {machine_core} has {len(mutants)} mutants')
