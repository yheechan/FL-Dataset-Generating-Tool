import json
import random
import shutil
import torch
import pandas as pd
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader

import lib.config as config
from lib.utils import *
from ml.mlp_model import MLP_Model
from ml.dataset import FL_Dataset


class EngineBase:
    def __init__(
            self
    ):
        pass

    # ===============================
    # Infer with model
    # ===============================
    def start_testing(
            self, project_name, project_out_dir, raw_test_set, model, filename, params,
            line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
    ):
        print(f"[{project_name}] Start Testing...")
        size = len(raw_test_set)

        acc_5 = []
        acc_10 = []
        accuracy_results = {}

        # testing loop
        for idx, (subject, feature_csv) in enumerate(raw_test_set):
            target_name = f"{subject}-{feature_csv.name}"
            print(f"\nTesting {target_name} ({idx+1}/{size})")
            rank = self.test_instr(
                model, project_out_dir, subject, feature_csv, params,
                line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
            )
            print(f"\tRank: {rank}")

            accuracy_results[target_name] = rank

            if int(rank) <= 5:
                acc_5.append((subject, feature_csv.name))
            if int(rank) <= 10:
                acc_10.append((subject, feature_csv.name))

        print(f"acc@5: {len(acc_5)}")
        print(f"acc@5 perc.: {len(acc_5)/size}")
        print(f"acc@10: {len(acc_10)}")
        print(f"acc@10 perc.: {len(acc_10)/size}")

        print("Done!")

        # Save accuracy results
        self.write_test_accuracy_to_csv(project_out_dir, accuracy_results, filename)
        self.write_test_accuracy_to_txt(project_out_dir, acc_5, acc_10, size)
    
    def test_instr(
            self, model, project_out_dir, subject, feature_csv, params,
            line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
        ):
        bug_id = feature_csv.name.split(".")[0]
        buggy_line_key = self.get_buggy_line_key(bug_keys_dir, subject, bug_id)
        # print(f"\tBuggy Line Key: {buggy_line_key}")

        # 1. Dataset Making
        test_dataset = FL_Dataset("test", [(subject, feature_csv)])

        # 2. DataLoader Making
        test_loader = DataLoader(
            test_dataset, batch_size=params["training_param"]["batch_size"], shuffle=False
        )

        # 3. Testing
        line_susp = self.infer_with_model(model, test_loader, params["training_param"]["device"])

        # 4. write line_susp to csv
        # key: susp. score
        line_susp_file = self.write_line_susp_scores(
            line_suspend_score_dir, line_susp, subject, bug_id
        )

        # 5. get rank of buggy function
        function_susp = self.get_function_level_results(line_susp, buggy_line_key)

        # 6. write function_susp to csv
        # [function_name, {susp.: susp. score, rank: rank}]
        self.write_function_susp_scores(function_susp_score_dir, function_susp, subject, bug_id)

        # 7. get rank of buggy function
        rank = self.get_rank_of_buggy_function(function_susp, buggy_line_key)

        return rank

    def infer_with_model(self, model, dataset, device):
        model.eval()
        with torch.no_grad():
            line_susp = {}

            for i, (key, features, label) in enumerate(dataset):
                features = features.to(device)
                label = label.to(device)

                label = label.view(-1, 1)

                output = model(features)

                for k, y in zip(key, output):
                    line_susp[k] = y.item()
        
        return line_susp

    # ===============================
    # Util API
    # ===============================
    def get_buggy_line_key(self, bug_keys_dir, subject, bug_id):
        buggy_line_key_txt = bug_keys_dir / f"{subject}-{bug_id}.buggy_line_key.txt"
        assert buggy_line_key_txt.exists(), f"Error: {buggy_line_key_txt} does not exist."
        
        with open(buggy_line_key_txt, "r") as f:
            buggy_line_key = f.readlines()[0].strip()
        return buggy_line_key
    
    def get_function_level_results(
            self, line_susp, buggy_line_key
    ):
        buggy_target_file = buggy_line_key.split("#")[0].split("/")[-1]
        buggy_function_name = buggy_line_key.split("#")[1]
        buggy_lineno = int(buggy_line_key.split("#")[-1])

        function_susp = {}
        for key, susp in line_susp.items():
            target_file = key.split("#")[0].split("/")[-1]
            function_name = key.split("#")[1]
            lineno = int(key.split("#")[-1])

            if function_name not in function_susp:
                function_susp[function_name] = {"susp.": susp}
            else:
                function_susp[function_name]["susp."] = max(function_susp[function_name]["susp."], susp)
        
        function_susp = sorted(
            function_susp.items(),
            key=lambda x: x[1]["susp."], reverse=True
        )

        function_susp = [
            (function_name, susp_dict["susp."]) for function_name, susp_dict in function_susp
        ]
        function_susp = pd.DataFrame(
            function_susp, columns=["function", "susp."]
        )
        function_susp = function_susp.sort_values(
            by="susp.", ascending=False
        ).reset_index(drop=True)
        function_susp["rank"] = function_susp["susp."].rank(
            ascending=False, method="max"
        ).astype(int)

        function_susp = [
            (function_name, {"susp.": susp, "rank": rank})
            for function_name, susp, rank in zip(
                function_susp["function"],
                function_susp["susp."],
                function_susp["rank"]
            )
        ]

        return function_susp

    def get_rank_of_buggy_function(self, function_susp, buggy_line_key):
        buggy_target_file = buggy_line_key.split("#")[0].split("/")[-1]
        buggy_function_name = buggy_line_key.split("#")[1]
        buggy_lineno = int(buggy_line_key.split("#")[-1])

        for i, (function_name, susp_dict) in enumerate(function_susp):
            if function_name == buggy_function_name:
                rank = susp_dict["rank"]
                return rank
        print(f"Error: {buggy_function_name} not found in function_susp.")
        return None

    def set_random_seed(self, seed):
        config.set_seed(seed)

    # ===============================
    # get/read/initalize/load
    # ===============================
    def get_project_dir(self, project_name):
        project_dir = out_dir / project_name
        if not project_dir.exists():
            return None
        return project_dir
    
    def initialize_project_directory(self, project_name):
        project_dir = out_dir / project_name / "train"
        project_dir.mkdir(parents=True, exist_ok=True)

        model_line_susp_score_dir = project_dir / "model_line_susp_score"
        model_line_susp_score_dir.mkdir(parents=True, exist_ok=True)

        model_function_susp_score_dir = project_dir / "model_function_susp_score"
        model_function_susp_score_dir.mkdir(parents=True, exist_ok=True)

        bug_keys_dir = project_dir / "bug_keys"
        bug_keys_dir.mkdir(parents=True, exist_ok=True)

        return project_dir, model_line_susp_score_dir, model_function_susp_score_dir, bug_keys_dir

    def read_parameter_file(self, project_dir):
        param_file = project_dir / "parameters.json"
        assert param_file.exists(), f"Parameter file {param_file} does not exist."
        with open(param_file, "r") as f:
            param_dict = json.load(f)
        return param_dict
    
    def get_model(self, project_out_dir, model, project_name):
        model_file = project_out_dir / f"{project_name}.pth"
        assert model_file.exists(), f"Model file {model_file} does not exist."
        model.load_state_dict(torch.load(model_file))
        return model

    def initialize_test_dirs(self, project_out_dir, inference_name):
        project_out_dir = project_out_dir / inference_name

        test_line_susp_score_dir = project_out_dir / "test_line_susp_score"
        test_line_susp_score_dir.mkdir(parents=True, exist_ok=True)

        test_function_susp_score_dir = project_out_dir / "test_function_susp_score"
        test_function_susp_score_dir.mkdir(parents=True, exist_ok=True)

        test_bug_keys_dir = project_out_dir / "test_bug_keys"
        test_bug_keys_dir.mkdir(parents=True, exist_ok=True)

        return project_out_dir, test_line_susp_score_dir, test_function_susp_score_dir, test_bug_keys_dir
    
    def load_model(self, params):
        model = MLP_Model(
            params["input_size"],
            params["hidden_size"],
            params["dropout"],
            params["stack_size"],
            params["output_size"]
        )
        return model
    # ===============================
    # Write/Save results
    # ===============================
    def write_parameter_file(self, project_dir, parameter_dict):
        param_file = project_dir / "parameters.json"
        with open(param_file, "w") as f:
            json.dump(parameter_dict, f, indent=4)
        return param_file
    
    def write_line_susp_scores(self, line_susp_dir, line_susp, subject, bug_id):
        line_susp_file = line_susp_dir / f"{subject}-{bug_id}.line_susp_score.csv"
        with open(line_susp_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "suspiciousness"])
            for key, susp in line_susp.items():
                writer.writerow([key, susp])
        return line_susp_file
    
    def write_function_susp_scores(self, function_susp_dir, function_susp, subject, bug_id):
        function_susp_file = function_susp_dir / f"{subject}-{bug_id}.function_susp_score.csv"
        with open(function_susp_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["function", "suspiciousness", "rank"])
            for function_name, susp_dict in function_susp:
                writer.writerow([function_name, susp_dict["susp."], susp_dict["rank"]])
        return function_susp_file

    def draw_loss_graph(self, project_out_dir, train_loss, validate_loss):
        plt.plot(train_loss, label="train loss")
        plt.plot(validate_loss, label="validate loss")
        plt.xlabel("epoch")
        plt.ylabel("loss")
        plt.legend()
        plt.savefig(project_out_dir / "loss_graph.png")
        plt.close()
    
    def write_loss_to_csv(self, project_out_dir, train_loss, validate_loss):
        loss_csv = project_out_dir / "train-validate-loss.csv"
        with open(loss_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["epoch", "train_loss", "validate_loss"])
            for epoch, train_l, val_l in zip(
                range(1, len(train_loss)+1), train_loss, validate_loss
            ):
                writer.writerow([epoch, train_l, val_l])
        return loss_csv

    def write_test_accuracy_to_csv(self, project_out_dir, accuracy_results, filename):
        accuracy_csv = project_out_dir / filename
        with open(accuracy_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["target", "rank"])
            for target, rank in accuracy_results.items():
                writer.writerow([target, rank])
        return accuracy_csv
    
    def save_model(self, project_out_dir, model, project_name):
        model_file = project_out_dir / f"{project_name}.pth"
        torch.save(model.state_dict(), model_file)
    
    def write_test_accuracy_to_txt(self, project_out_dir, acc_5, acc_10, size):
        fl_acc_txt = project_out_dir / "fl_acc.txt"
        with open(fl_acc_txt, "w") as f:
            f.write(f"Total # of bug versions: {size}\n")
            f.write(f"acc@5: {len(acc_5)}\n")
            f.write(f"acc@5 perc.: {len(acc_5)/size}\n")
            f.write(f"acc@10: {len(acc_10)}\n")
            f.write(f"acc@10 perc.: {len(acc_10)/size}")

    # ===============================
    # Related to dataset
    # ===============================
    def load_raw_dataset(self, dataset_pair_list, bug_keys_dir):
        raw_dataset = []

        for subject, dataset_name in dataset_pair_list:
            dataset_dir = out_dir / subject / dataset_name
            pp_fl_features_dir = dataset_dir / "PP_FL_features_per_bug_version"

            feature_csv_list = [
                f for f in pp_fl_features_dir.iterdir() if not f.is_dir() and f.suffix == ".csv"
            ]
            feature_csv_list = sorted(
                feature_csv_list, key=lambda x: int(x.name.split(".")[0][3:])
            )

            for feature_csv in feature_csv_list:
                self.copy_buggy_keys(subject, dataset_dir, feature_csv, bug_keys_dir)
                raw_dataset.append((subject, feature_csv))
        
        random.shuffle(raw_dataset)
        return raw_dataset
    
    def copy_buggy_keys(self, subject, dataset_dir, feature_csv, bug_keys_dir):
        bug_id = feature_csv.name.split(".")[0]
        buggy_line_key_txt = dataset_dir / "buggy_line_key_per_bug_version" / f"{bug_id}.buggy_line_key.txt"
        assert buggy_line_key_txt.exists(), f"Error: {buggy_line_key_txt} does not exist."

        assert bug_keys_dir.exists(), f"Error: {bug_keys_dir} does not exist."

        buggy_keys_csv = bug_keys_dir / f"{subject}-{buggy_line_key_txt.name}"
        shutil.copy(buggy_line_key_txt, buggy_keys_csv)
    
    def split_dataset(
            self, project_out_dir, dataset, train_ratio, val_ratio, test_ratio
    ):
        total_size = len(dataset)
        train_size = int(total_size * (train_ratio/10))
        val_size = int(total_size * (val_ratio/10))
        test_size = int(total_size * (test_ratio/10))

        raw_train_set = dataset[:train_size]
        raw_val_set = dataset[train_size:train_size+val_size]
        raw_test_set = dataset[train_size+val_size:]

        self.save_split_dataset(project_out_dir, raw_train_set, "train")
        self.save_split_dataset(project_out_dir, raw_val_set, "val")
        self.save_split_dataset(project_out_dir, raw_test_set, "test")

        return raw_train_set, raw_val_set, raw_test_set
    
    def save_split_dataset(self, project_out_dir, dataset, split_type):
        split_dir = project_out_dir / "split_dataset" / split_type
        split_dir.mkdir(exist_ok=True, parents=True)

        for subject, feature_csv in dataset:
            split_csv = split_dir / f"{subject}-{feature_csv.name}"
            shutil.copy(feature_csv, split_csv)
        
