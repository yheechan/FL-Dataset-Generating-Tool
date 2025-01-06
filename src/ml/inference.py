from torch.utils.data import DataLoader

from lib.utils import *
import lib.config as config
from ml.engine_base import EngineBase
from ml.dataset import FL_Dataset

class Inference(EngineBase):
    def __init__(
            self, project_name, dataset_pair_list,
            device, inference_name
    ):
        super().__init__()

        self.inference_name = inference_name
        self.project_name = project_name
        self.project_out_dir = self.get_project_dir(self.project_name)
        assert self.project_out_dir != None, f"Project {self.project_name} does not exist."

        self.params = self.read_parameter_file(self.project_out_dir / "train")
        self.params["config_param"]["project_name"] = project_name
        self.params["config_param"]["dataset_pair_list"] = dataset_pair_list
        self.params["training_param"]["device"] = device

        # set random seed
        self.set_random_seed(self.params["config_param"]["random_seed"])

        self.project_out_dir, \
        self.test_line_susp_score_dir, \
        self.test_function_susp_score_dir, \
        self.test_bug_keys_dir = self.initialize_test_dirs(self.project_out_dir, self.inference_name)
    
    def run(self):
        # 1. Load raw dataset
        self.raw_test_dataset = self.load_raw_dataset(
            self.params["config_param"]["dataset_pair_list"], self.test_bug_keys_dir
        )

        # 3. Load Model
        self.mlp_model = self.load_model(self.params["model_param"])
        self.mlp_model = self.get_model(self.project_out_dir.parent / "train", self.mlp_model, self.project_name)
        self.mlp_model.to(self.params["training_param"]["device"])
        print(f"Got model: {self.mlp_model}")

        # 4. Inference
        self.start_testing(
            self.project_name, self.project_out_dir,
            self.raw_test_dataset, self.mlp_model,
            "inference-accuracy.csv", self.params,
            self.test_line_susp_score_dir,
            self.test_function_susp_score_dir,
            self.test_bug_keys_dir
        )
            



