import multiprocessing
import subprocess as sp

from lib.utils import *

class FileManager():
    def __init__(self, subject_name, work, verbose=False):
        self.name = subject_name
        self.work_dir = work # PATH
        self.verbose = verbose
        self.experiment_config_dir = configs_dir

    # ++++++++++++++++++++++
    # +++++ COMMONS ++++++++
    # ++++++++++++++++++++++
    def collect_data_remote(self, data, dest, work_assignments):
        tasks = []
        machine_list = []
        for machine, works in work_assignments.items():
            machine, core, homedir = machine.split("::")
            if machine not in machine_list:
                machine_list.append(machine)
                tasks.append((machine, homedir, data, dest))

        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_collect_data_remote, tasks)
        print(f"Number of tasks (collect): {len(tasks)}")

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
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_src_remote, tasks)
        print(f"Number of tasks (src): {len(tasks)}")
    
    def single_send_src_remote(self, task):
        machine, homedir = task
        print_command([
            "rsync", "-t", "-r", f"{src_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{src_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ])
    
    def make_assigned_works_dir_remote(self, machinesCores_list, stage):
        tasks = []
        for machine, core, homedir in machinesCores_list:
            tasks.append((machine, core, homedir, stage))

        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_assigned_works_dir_remote, tasks)
        print(f"Number of tasks (assigned_works): {len(tasks)}")

    def single_assigned_works_dir_remote(self, task):
        machine, core, homedir, stage = task
        print_command([
            "ssh", f"{machine}",
            f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works"
        ], self.verbose)
        sp.check_call([
            "ssh", f"{machine}",
            f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works"
        ])
    
    def send_works_remote(self, work_assignments, stage, dir_form=False):
        # work_assignments format: {machine_core: [(version_name, buggy_code_file_path), ...]}
        tasks = []
        for machine_core, work_infos in work_assignments.items():
            machine, core, homedir = machine_core.split("::")

            for work_info in work_infos:
                tasks.append((machine, core, homedir, stage, work_info, dir_form))
        
        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_work_remote, tasks)
        print(f"Number of tasks (works): {len(tasks)}")
    
    def single_send_work_remote(self, task):
        machine, core, homedir, stage, work_info, dir_form = task
        if dir_form:
            print_command([
            "rsync", "-t", "-r", f"{work_info}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works"
            ], self.verbose)
            sp.check_call([
                "rsync", "-t", "-r", f"{work_info}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works"
            ])  
        else:
            version_name = work_info[0]
            buggy_code_file_path = work_info[1]

            # initialize verison directory
            print_command([
                "ssh", f"{machine}",
                f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works/{version_name}/buggy_code_file"
            ], self.verbose)
            sp.check_call([
                "ssh", f"{machine}",
                f"mkdir -p {homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works/{version_name}/buggy_code_file"
            ])


            # send buggy code file
            print_command([
                "rsync", "-t", "-r", f"{buggy_code_file_path}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works/{version_name}/buggy_code_file"
            ], self.verbose)
            sp.check_call([
                "rsync", "-t", "-r", f"{buggy_code_file_path}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}-assigned_works/{version_name}/buggy_code_file"
            ])


    def send_repo_remote(self, repo, machinesCores_list):
        # machinesCores_list format: [(machine, core, homedir), ...]
        tasks = []
        for machine, core, homedir in machinesCores_list:
            tasks.append((machine, core, homedir, repo))

        limit = 50
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_repo_remote, tasks)
        print(f"Number of tasks (repo): {len(tasks)}")

    def single_send_repo_remote(self, task):
        machine, core, homedir, repo = task
        print_command([
            "rsync", "-t", "-r", f"{repo}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}"
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
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_configurations_remote, tasks)
        print(f"Number of tasks (configurations): {len(tasks)}")
    
    def single_send_configurations_remote(self, task):
        machine, homedir = task
        print_command([
            "rsync", "-t", "-r", f"{self.work_dir}/configurations.json", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{self.work_dir}/configurations.json", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ])


    def send_experiment_configurations_remote(self, machinesCores_dict):
        # machinesCores_dict format: {machine_name: [(core, homedir), ...]}
        tasks = []
        for machine, coreHomedir_list in machinesCores_dict.items():
            homedir = coreHomedir_list[0][1]
            tasks.append((machine, homedir))

        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_experiment_configurations_remote, tasks)
        print(f"Number of tasks (configurations): {len(tasks)}")
    
    def single_send_experiment_configurations_remote(self, task):
        machine, homedir = task
        print_command([
            "rsync", "-t", "-r", f"{self.experiment_config_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{self.experiment_config_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}"
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
    
    def send_tools_remote(self, tools_dir, machinesCores_dict):
        # machinesCores_dict format: {machine_name: [(core, homedir), ...]}
        tasks = []
        for machine, coreHomedir_list in machinesCores_dict.items():
            homedir = coreHomedir_list[0][1]
            tasks.append((machine, homedir, tools_dir))

        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_tools_remote, tasks)
        print(f"Number of tasks (tools): {len(tasks)}")
    
    def single_send_tools_remote(self, task):
        machine, homedir, tools_dir = task
        print_command([
            "rsync", "-t", "-r", f"{tools_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{tools_dir}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}"
        ])
    

    


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

        limit = 100
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_assigned_dir_stage01, tasks)
        print(f"Number of tasks (assigned-stage01): {len(tasks)}")
    
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
        with multiprocessing.Pool(processes=limit) as pool:
            pool.map(self.single_send_mutant_stage01, tasks)
        print(f"Number of tasks (mutants-stage01): {len(tasks)}")
    
    def single_send_mutant_stage01(self, task):
        machine, core, homedir, stage, target_dir, mutant = task
        print_command([
            "rsync", "-t", "-r", f"{mutant}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ], self.verbose)
        sp.check_call([
            "rsync", "-t", "-r", f"{mutant}", f"{machine}:{homedir}FL-dataset-generation-{self.name}/work/{self.name}/working_env/{machine}/{core}/{stage}/{target_dir}"
        ])
