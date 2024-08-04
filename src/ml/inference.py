from lib.utils import *
import lib.config as config
from ml.engine_base import EngineBase

class Inference(EngineBase):
    def __init__(
            self, model_name, dataset_pair_list
    ):
        super().__init__()

        self.project_name = model_name
        self.project_out_dir = self.get_project_dir(self.project_name)
        assert self.project_out_dir != None, f"Project {self.project_name} does not exist."

        self.params = self.read_parameter_file(self.project_out_dir)

        # set random seed
        self.set_random_seed(self.params["random_seed"])

