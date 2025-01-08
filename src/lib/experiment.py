import json

from lib.utils import *

class Experiment():
    def __init__(self):
        self.experiment_config = self.read_experiment_config("config.json")
        self.use_distributed_machines = self.experiment_config["use_distributed_machines"]

        # self.machines format: [(machine_name, core_idx, homedirectory)]
        self.machineCores_list = self.read_machines()

        # self.machine_core_dict format: {machine_name: [core_idx, homedirectory]}
        self.machineCores_dict = self.get_machine_core_dict()
    
    def get_machine_core_dict(self):
        machineCores_dict = {}
        for machine_name, core_idx, homedirectory in self.machineCores_list:
            if machine_name not in machineCores_dict:
                machineCores_dict[machine_name] = []
            machineCores_dict[machine_name].append((core_idx, homedirectory))
        return machineCores_dict
    
    def read_experiment_config(self, config_file):
        configs = None
        config_json = configs_dir / config_file
        
        with config_json.open() as f:
            configs = json.load(f)
        
        if configs is None:
            raise Exception("Configurations are not loaded")

        return configs

    def read_machines(self):
        machineCores_list = []

        if self.use_distributed_machines:
            machines = None

            machines_json = configs_dir / "machines.json"
            with machines_json.open() as f:
                machines = json.load(f)
            
            if machines is None:
                raise Exception("Machines are not loaded")
            
            for machine_name, info in machines.items():
                cores = info["cores"]
                homedirectory = info["homedirectory"]

                for idx in range(cores):
                    core_idx = f"core{idx}"
                    machineCores_list.append((machine_name, core_idx, homedirectory))
        else:
            single_machine = self.experiment_config["single_machine"]
            machine_name = single_machine["name"]
            cores = single_machine["cores"]
            homedirectory = single_machine["homedirectory"]

            for idx in range(cores):
                core_idx = f"core{idx}"
                machineCores_list.append((machine_name, core_idx, homedirectory))

        return machineCores_list
            
    def print_machines(self):
        print(f"Number of machines: {len(self.machineCores_list)}")
        for machine in self.machineCores_list:
            print(f"\t{machine}")

    def init_analysis_config(self):
        self.analysis_config = self.read_experiment_config("analysis_config.json")