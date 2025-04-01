from torch.utils.data import DataLoader

from lib.utils import *
import lib.config as config
from ml.engine_base import EngineBase
from ml.dataset import FL_Dataset

from analysis.analysis_utils import *
from lib.experiment import Experiment
from lib.database import CRUD

class Inference(EngineBase):
    def __init__(
            self, subject_name, experiment_name,
            targeting_experiment_name,
            model_name,
            device, inference_name
    ):
        super().__init__()

        self.subject_name = subject_name
        self.experiment_name = experiment_name
        self.targeting_experiment_name = targeting_experiment_name

        self.inference_name = inference_name
        self.model_subject_name = model_name.split("::")[0]
        self.model_name = model_name.split("::")[-1]
        self.project_out_dir = self.get_project_dir(self.model_subject_name, self.model_name)
        assert self.project_out_dir != None, f"Project {model_name} does not exist."

        self.params = self.read_parameter_file(self.project_out_dir / "train")
        self.params["config_param"]["target_subject_name"] = self.subject_name
        self.params["config_param"]["target_experiment_name"] = self.experiment_name
        if "calib3d_TF_top30" in self.subject_name:
            self.params["config_param"]["target_experiment_name"] = "TF_top30"
        self.params["config_param"]["targeting_experiment_name"] = self.targeting_experiment_name
        self.params["training_param"]["device"] = device

        # set random seed
        self.set_random_seed(self.params["config_param"]["random_seed"])

        self.project_out_dir, \
        self.test_line_susp_score_dir, \
        self.test_function_susp_score_dir, \
        self.test_bug_keys_dir = self.initialize_test_dirs(self.project_out_dir, self.inference_name)

        self.experiment = Experiment()
        # Settings for database
        self.host = self.experiment.experiment_config["database"]["host"]
        self.port = self.experiment.experiment_config["database"]["port"]
        self.user = self.experiment.experiment_config["database"]["user"]
        self.password = self.experiment.experiment_config["database"]["password"]
        self.database = self.experiment.experiment_config["database"]["database"]

        self.db = CRUD(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
    
    def run(self):
        # 0. get target buggy version list
        buggy_version_list = get_target_buggy_version_list(
            self.params["config_param"]["target_subject_name"],
            self.params["config_param"]["target_experiment_name"],
            "mbfl",
            self.db
        )

        print(f"Got buggy version list: {len(buggy_version_list)}")

        target_features_dir = out_dir / self.params["config_param"]["target_subject_name"] / "analysis" / self.params["config_param"]["targeting_experiment_name"] / "fl_features"
        assert target_features_dir.exists(), f"Features directory does not exist: {target_features_dir}"

        # 1. Load raw dataset
        self.raw_test_dataset, self.bug_key_map = self.load_raw_dataset(
            buggy_version_list, target_features_dir
        )
        print(f"Loaded raw dataset: {len(self.raw_test_dataset)}")

        # 3. Load Model
        self.mlp_model = self.load_model(self.params["model_param"])
        self.mlp_model = self.get_model(self.project_out_dir.parent.parent / "train", self.mlp_model, self.model_name)
        self.mlp_model.to(self.params["training_param"]["device"])
        print(f"Got model: {self.mlp_model}")

        # 4. Inference
        self.start_testing(
            self.subject_name, self.experiment_name, self.project_out_dir,
            self.bug_key_map,
            self.raw_test_dataset, self.mlp_model,
            "inference-accuracy.csv", self.params,
            self.test_line_susp_score_dir,
            self.test_function_susp_score_dir,
            self.test_bug_keys_dir
        )
            



