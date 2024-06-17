import multiprocessing
import subprocess as sp

from lib.utils import *

class FileManager():
    def __init__(self, subject_name, work, verbose=False):
        self.name = subject_name
        self.work_dir = work # PATH
        self.verbose = verbose

    # ++++++++++++++++++++++
    # +++++ COMMONS ++++++++
    # ++++++++++++++++++++++
    def collect_data_remote(self, data, dest, machinesCores_dict):
        tasks = []
        for machine, coreHomedir_list in machinesCores_dict.items():
            homedir = coreHomedir_list[0][1]
            tasks.append((machine, homedir, data, dest))

        limit = 100
        print(f"Number of tasks (collect): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_collect_data_remote, tasks)

    def single_collect_data_remote(self, task):
        machine, homedir, data, dest = task
        print_command([
            "rsync", "-t", "-r", "--no-implied-dirs", f"{machine}:{homedir}FL-dataset-generation-{self.name}/out/{self.name}/{data}/", f"{dest}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", "--no-implied-dirs", f"{machine}:{homedir}FL-dataset-generation-{self.name}/out/{self.name}/{data}/", f"{dest}"
        ])
        
    def send_src_remote(self, machinesCores_dict):
        # machinesCores_dict format: {machine_name: [(core, homedir), ...]}
        tasks = []
        for machine, coreHomedir_list in machinesCores_dict.items():
            homedir = coreHomedir_list[0][1]
            tasks.append((machine, homedir))

        limit = 100
        print(f"Number of tasks (src): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_src_remote, tasks)
    
    def single_send_src_remote(self, task):
        machine, homedir = task
        print_command([
            "rsync", "-t", "-r", f"{src_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{src_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ])

    def send_repo_remote(self, repo, machinesCores_list):
        # machinesCores_list format: [(machine, core, homedir), ...]
        tasks = []
        for machine, core, homedir in machinesCores_list:
            tasks.append((machine, core, homedir, repo))

        limit = 100
        print(f"Number of tasks (repo): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_repo_remote, tasks)

    def single_send_repo_remote(self, task):
        machine, core, homedir, repo = task
        print_command([
            "rsync", "-t", "-r", f"{repo}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{repo}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}"
        ])
    
    def send_configurations_remote(self, machinesCores_dict):
        # machinesCores_dict format: [(machine, core, homedir), ...]
        tasks = []
        for machine, coreHomedir_list in machinesCores_dict.items():
            homedir = coreHomedir_list[0][1]
            tasks.append((machine, homedir))

        limit = 100
        print(f"Number of tasks (configurations): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_configurations_remote, tasks)
    
    def single_send_configurations_remote(self, task):
        machine, homedir = task
        print_command([
            "rsync", "-t", "-r", f"{self.work_dir}/configurations.json", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{self.work_dir}/configurations.json", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ])

    def make_working_env_local(self):
        self.working_env = self.work_dir / "working_env"
        print_command(["mkdir", "-p", self.working_env], self.verbose)
        self.working_env.mkdir(exist_ok=True, parents=True)
        return self.working_env

    def make_output_dir(self, output_name):
        self.output_dir = out_dir / f"{self.name}" / output_name
        print_command(["mkdir", "-p", self.output_dir], self.verbose)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        return self.output_dir
    


    # +++++++++++++++++++
    # +++++ STAGE01 +++++
    # +++++++++++++++++++
    def make_assigned_works_remote_stage01(self, mutant_assignments):
        # mutant_assignments format: {machine_core: [(target_file, mutant), ...]}
        tasks = []
        machine_targetDir = {}
        for machine_core, assignments in mutant_assignments.items():
            machine, core, homedir = machine_core.split("::")
            machieCore = f"{machine}::{core}"

            for target_file, mutant in assignments:
                target_dir = mutant.parent.name

                if machieCore not in machine_targetDir:
                    machine_targetDir[machieCore] = []

                if target_dir not in machine_targetDir[machieCore]:
                    machine_targetDir[machieCore].append(target_dir)
                    tasks.append((machine, core, homedir, "stage01-assigned_works", target_dir))

        limit = 50
        print(f"Number of tasks (assigned-stage01): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_assigned_dir_stage01, tasks)
    
    def single_assigned_dir_stage01(self, task):
        machine, core, homedir, stage, target_dir = task
        print_command([
            "ssh", f"{machine}",
            f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ], self.verbose)
        sp.check_call([
            "ssh", f"{machine}",
            f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ])
    
    def send_mutants_remote_stage01(self, mutant_assignments):
        # mutant_assignments format: {machine_core: [(target_file, mutant), ...]}
        tasks = []
        for machine_core, assignments in mutant_assignments.items():
            machine, core, homedir = machine_core.split("::")

            for target_file, mutant in assignments:
                target_dir = mutant.parent.name

                tasks.append((machine, core, homedir, "stage01-assigned_works", target_dir, mutant))
        
        limit = 100
        print(f"Number of tasks (mutants-stage01): {len(tasks)}")
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_mutant_stage01, tasks)
    
    def single_send_mutant_stage01(self, task):
        machine, core, homedir, stage, target_dir, mutant = task
        print_command([
            "rsync", "-t", "-r", f"{mutant}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{mutant}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ])
    