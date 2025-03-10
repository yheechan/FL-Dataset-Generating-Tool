import json
import random
import shutil
import torch
import pandas as pd
import matplotlib.pyplot as plt # 2024-08-08
from torch.utils.data import DataLoader

import lib.config as config
from lib.utils import *
from ml.mlp_model import MLP_Model
from ml.dataset import FL_Dataset

from lib.susp_score_formula import *
from lib.database import CRUD


class EngineBase:
    def __init__(
            self
    ):
        pass

    # ===============================
    # Infer with model
    # ===============================
    def start_testing(
            self, subject_name, experiment_name, project_out_dir, bug_key_map, raw_test_set, model, filename, params,
            line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
    ):
        print(f"[{subject_name}] Start Testing...")
        size = len(raw_test_set)

        acc_5 = []
        acc_10 = []
        accuracy_results = {}

        # testing loop
        for idx, bug_idx in enumerate(raw_test_set):
            version_name = bug_key_map[bug_idx]["version"]
            buggy_line_key = bug_key_map[bug_idx]["buggy_line_key"]
            target_name = f"{subject_name}-{version_name}"

            print(f"\nTesting {target_name} ({idx+1}/{size})")
            rank = self.test_instr(
                model, subject_name, buggy_line_key, bug_idx, version_name, raw_test_set[bug_idx], params,
                line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
            )
            print(f"\tRank: {rank}")

            accuracy_results[target_name] = rank

            if int(rank) <= 5:
                acc_5.append((subject_name, version_name))
            if int(rank) <= 10:
                acc_10.append((subject_name, version_name))

        print(f"acc@5: {len(acc_5)}")
        print(f"acc@5 perc.: {len(acc_5)/size}")
        print(f"acc@10: {len(acc_10)}")
        print(f"acc@10 perc.: {len(acc_10)/size}")

        print("Done!")

        # Save accuracy results
        self.write_test_accuracy_to_csv(project_out_dir, accuracy_results, filename)
        self.write_test_accuracy_to_txt(project_out_dir, acc_5, acc_10, size)
    
    def test_instr(
            self, model, subject_name, buggy_line_key, bug_idx, version_name, raw_test, params,
            line_suspend_score_dir, function_susp_score_dir, bug_keys_dir
        ):
        # print(f"\tBuggy Line Key: {buggy_line_key}")

        # 1. Dataset Making
        test_dataset = FL_Dataset("test", {bug_idx: raw_test})

        # 2. DataLoader Making
        test_loader = DataLoader(
            test_dataset, batch_size=params["training_param"]["batch_size"], shuffle=False
        )

        # 3. Testing
        line_susp = self.infer_with_model(model, test_loader, params["training_param"]["device"])

        # 4. write line_susp to csv
        # key: susp. score
        line_susp_file = self.write_line_susp_scores(
            line_suspend_score_dir, line_susp, subject_name, bug_idx, version_name
        )

        # 5. get rank of buggy function
        function_susp = self.get_function_level_results(line_susp, buggy_line_key)

        # 6. write function_susp to csv
        # [function_name, {susp.: susp. score, rank: rank}]
        self.write_function_susp_scores(function_susp_score_dir, function_susp, subject_name, bug_idx, version_name)

        # 7. get rank of buggy function
        rank = self.get_rank_of_buggy_function(function_susp, buggy_line_key)

        return rank

    def infer_with_model(self, model, dataset, device):
        model.eval()
        with torch.no_grad():
            line_susp = {}

            for i, (key, features, label, line_key) in enumerate(dataset):
                features = features.to(device)
                label = label.to(device)

                label = label.view(-1, 1)

                output = model(features)

                for k, y in zip(line_key, output):
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
            file_func_key = f"{target_file}#{function_name}"

            if file_func_key not in function_susp:
                function_susp[file_func_key] = {"susp.": susp}
            else:
                function_susp[file_func_key]["susp."] = max(function_susp[file_func_key]["susp."], susp)
        
        function_susp = sorted(
            function_susp.items(),
            key=lambda x: x[1]["susp."], reverse=True
        )

        function_susp = [
            (file_func_key, susp_dict["susp."]) for file_func_key, susp_dict in function_susp
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
            (file_func_key, {"susp.": susp, "rank": rank})
            for file_func_key, susp, rank in zip(
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

        buggy_file_func_key = f"{buggy_target_file}#{buggy_function_name}"

        for i, (file_func_key, susp_dict) in enumerate(function_susp):
            if file_func_key == buggy_file_func_key:
                rank = susp_dict["rank"]
                return rank
        print(f"Error: {buggy_file_func_key} not found in function_susp.")
        return None

    def set_random_seed(self, seed):
        config.set_seed(seed)

    # ===============================
    # get/read/initalize/load
    # ===============================
    def get_project_dir(self, subject_name, project_name):
        project_dir = out_dir / subject_name / "analysis/ml" / project_name
        if not project_dir.exists():
            return None
        return project_dir
    
    def initialize_project_directory(self, subject_name, project_name):
        project_dir = out_dir / subject_name / "analysis/ml" / project_name / "train"
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
        if "/" in project_name:
            project_name = project_name.replace("/", "-")
        model_file = project_out_dir / f"{project_name}.pth"
        assert model_file.exists(), f"Model file {model_file} does not exist."
        model.load_state_dict(torch.load(model_file))
        return model

    def initialize_test_dirs(self, project_out_dir, inference_name):
        project_out_dir = project_out_dir / "inference" / inference_name

        test_line_susp_score_dir = project_out_dir / "test_line_susp_score"
        test_line_susp_score_dir.mkdir(parents=True, exist_ok=True)

        test_function_susp_score_dir = project_out_dir / "test_function_susp_score"
        test_function_susp_score_dir.mkdir(parents=True, exist_ok=True)

        test_bug_keys_dir = project_out_dir / "test_bug_keys"
        test_bug_keys_dir.mkdir(parents=True, exist_ok=True)

        return project_out_dir, test_line_susp_score_dir, test_function_susp_score_dir, test_bug_keys_dir
    
    def load_model(self, params):
        model = MLP_Model(
            params["model_shape"],
            params["dropout"],
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
    
    def write_line_susp_scores(self, line_susp_dir, line_susp, subject, bug_id, version_name):
        line_susp_file = line_susp_dir / f"{subject}-{version_name}-{bug_id}.line_susp_score.csv"
        with open(line_susp_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "suspiciousness"])
            for key, susp in line_susp.items():
                writer.writerow([key, susp])
        return line_susp_file
    
    def write_function_susp_scores(self, function_susp_dir, function_susp, subject, bug_id, version_name):
        function_susp_file = function_susp_dir / f"{subject}-{version_name}-{bug_id}.function_susp_score.csv"
        with open(function_susp_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["file_function_key", "suspiciousness", "rank"])
            for file_func_key, susp_dict in function_susp:
                writer.writerow([file_func_key, susp_dict["susp."], susp_dict["rank"]])
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
        if "/" in project_name:
            project_name = project_name.replace("/", "-")
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
    def load_raw_dataset(self, buggy_version_list, features_dir):
        raw_dataset = {}
        fl_features = ["ep", "ef", "np", "nf"]
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            fl_features.extend(sub_form_list)
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            fl_features.extend(sub_form_list)
        columns = ["file", "function", "lineno", "is_buggy_line"] + fl_features

        bug_key_map = {}
        for bug_data in buggy_version_list:
            bug_idx = bug_data[0]
            version = bug_data[1]
            buggy_file = bug_data[2]
            buggy_function = bug_data[3]
            buggy_lineno = bug_data[4]
            bug_key_map[bug_idx] = {
                "version": bug_data[1],
                "buggy_line_key": f"{buggy_file}#{buggy_function}#{buggy_lineno}"
            }

            csv_file = features_dir / f"{version}.csv"
            assert csv_file.exists(), f"Error: {csv_file} does not exist."
            with open(csv_file, "r") as f:
                reader = csv.reader(f)
                next(reader)
                for line in reader:
                    line_data = {}
                    for index, feature_name in enumerate(columns):
                        line_data[feature_name] = line[index]
                    if bug_idx not in raw_dataset:
                        raw_dataset[bug_idx] = []
                    raw_dataset[bug_idx].append(line_data)
                
        return raw_dataset, bug_key_map
    
    def split_dataset(
            self, dataset, train_ratio, val_ratio, test_ratio
    ):
        total_size = len(dataset.keys())
        train_size = int(total_size * (train_ratio/10))
        val_size = int(total_size * (val_ratio/10))
        test_size = int(total_size * (test_ratio/10))

        keys = list(dataset.keys())
        random.shuffle(keys)

        train_keys = keys[:train_size]
        val_keys = keys[train_size:train_size+val_size]
        test_keys = keys[train_size+val_size:]

        raw_train_set = {}
        raw_val_set = {}
        raw_test_set = {}

        for key in train_keys:
            raw_train_set[key] = dataset[key]
        for key in val_keys:
            raw_val_set[key] = dataset[key]
        for key in test_keys:
            raw_test_set[key] = dataset[key]

        return raw_train_set, raw_val_set, raw_test_set
    
    def save_split_dataset(self, project_out_dir, dataset, split_type):
        split_dir = project_out_dir / "split_dataset" / split_type
        split_dir.mkdir(exist_ok=True, parents=True)

        for subject, feature_csv in dataset:
            split_csv = split_dir / f"{subject}-{feature_csv.name}"
            shutil.copy(feature_csv, split_csv)
        
