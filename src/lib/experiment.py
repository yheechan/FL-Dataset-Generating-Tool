import json

from lib.utils import *

class Experiment():
    def __init__(self):
        self.experiment_config = self.read_experiment_config()
        self.use_distributed_machines = self.experiment_config["use_distributed_machines"]

        # self.machines format: [(machine_name, core_idx, homedirectory)]
        self.machines = self.read_machines()
    
    def read_experiment_config(self):
        configs = None
        config_json = configs_dir / "config.json"
        
        with config_json.open() as f:
            configs = json.load(f)
        
        if configs is None:
            raise Exception("Configurations are not loaded")

        return configs

    def read_machines(self):
        if self.use_distributed_machines:
            machines = None

            machines_json = configs_dir / "machines.json"
            with machines_json.open() as f:
                machines = json.load(f)
            
            if machines is None:
                raise Exception("Machines are not loaded")
            
            machines_cores_list = []
            for machine_name, info in machines.items():
                cores = info["cores"]
                homedirectory = info["homedirectory"]

                for idx in range(cores):
                    core_idx = f"core{idx}"
                    machines_cores_list.append((machine_name, core_idx, homedirectory))
        else:
            single_machine = self.experiment_config["single_machine"]
            machine_name = single_machine["name"]
            cores = single_machine["cores"]
            homedirectory = single_machine["homedirectory"]

            machines_cores_list = []
            for idx in range(cores):
                core_idx = f"core{idx}"
                machines_cores_list.append((machine_name, core_idx, homedirectory))

        return machines_cores_list
            
    def print_machines(self):
        print(f"Number of machines: {len(self.machines)}")
        for machine in self.machines:
            print(f"\t{machine}")
