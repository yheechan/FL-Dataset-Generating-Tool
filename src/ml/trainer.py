import random
import shutil
from torch.utils.data import DataLoader
import torch
import numpy as np
import json
import torch.nn as nn
import pandas as pd

from lib.utils import *
import lib.config as config
from ml.dataset import FL_Dataset
from ml.mlp_model import MLP_Model

class Trainer:
    def __init__(self, 
                 # config param
                 project_name, dataset_pair_list,
                 train_ratio, validate_ratio, test_ratio,
                 random_seed=42,
                 # training param
                 epoch=3, batch_size=64, learning_rate=1e-3, device="cuda",
                 # model param
                 input_size=35, hidden_size=64, dropout=0.2, stack_size=3, output_size=1):
        
        # config param
        self.random_seed = random_seed
        config.set_seed(self.random_seed)

        self.project_name = project_name
        self.project_out_dir = out_dir / self.project_name
        # assert not self.project_out_dir.exists(), f"Error: {self.project_out_dir} already exists."
        self.project_out_dir.mkdir(exist_ok=True, parents=True)

        self.model_line_susp_score_dir = self.project_out_dir / "model_line_susp_score"
        self.model_line_susp_score_dir.mkdir(exist_ok=True, parents=True)

        self.model_function_susp_score_dir = self.project_out_dir / "model_function_susp_score"
        self.model_function_susp_score_dir.mkdir(exist_ok=True, parents=True)

        self.dataset_pair_list = dataset_pair_list
        self.train_ratio = train_ratio
        self.validate_ratio = validate_ratio
        self.test_ratio = test_ratio

        # training param
        self.epoch = epoch
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = device

        # model param
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.dropout = dropout
        self.stack_size = stack_size
        self.output_size = output_size
    
    def run(self):
        # 0. Save Parameter as json
        self.save_parameters()

        # 1. Dataset Splitting
        self.raw_dataset = self.load_raw_dataset()
        self.split_dataset()

        # 2. Dataset Making
        self.train_dataset = FL_Dataset("train", self.raw_train_set)
        self.validate_dataset = FL_Dataset("validate", self.raw_validate_set)
        print(f"Made datasets: train({len(self.train_dataset)}), validate({len(self.validate_dataset)})")

        # 3. DataLoader Making
        self.train_loader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)
        self.validate_loader = DataLoader(self.validate_dataset, batch_size=self.batch_size, shuffle=False)
        print(f"Made loaders: train({len(self.train_loader)}), validate({len(self.validate_loader)})")

        # 4. Model Making
        self.mlp_model = MLP_Model(
            self.input_size,
            self.hidden_size,
            self.dropout,
            self.stack_size,
            self.output_size
        )
        self.mlp_model.to(self.device)
        print(f"Made model: {self.mlp_model}")
        
        # 5. loss and optimizer
        # self.loss_fn = nn.CrossEntropyLoss()
        print(f"weight: {self.train_dataset.weight}")
        pos_weight = torch.tensor(self.train_dataset.pos_weight).to(self.device)
        self.loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        # self.loss_fn = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.SGD(self.mlp_model.parameters(), lr=self.learning_rate)

        # 6. Training
        self.start_training()

        # 7. Testing
        self.start_testing()

    
    def start_training(self):
        print(f"[{self.project_name}] Training model for {self.epoch} epochs...")
        for epoch in range(self.epoch):
            print(f"\nEpoch {epoch+1}/{self.epoch}")
            avg_train_loss = self.train_loop()
            avg_validate_loss = self.validate_loop()
        print("Done!")
    
    def start_testing(self):
        print(f"[{self.project_name}] Testing model...")
        size = len(self.raw_test_set)

        acc_5 = []
        acc_10 = []

        for idx, (subject, feature_csv) in enumerate(self.raw_test_set):
            print(f"\nTesting {subject}-{feature_csv.name} ({idx+1}/{size})")
            rank = self.test_instr(subject, feature_csv)
            print(f"\tRank: {rank}")

            if int(rank) <= 5:
                acc_5.append((subject, feature_csv.name))
            if int(rank) <= 10:
                acc_10.append((subject, feature_csv.name))
        
        print(f"acc@5: {len(acc_5)}")
        print(f"acc@5 perc.: {len(acc_5)/size}")
        print(f"acc@10: {len(acc_10)}")
        print(f"acc@10 perc.: {len(acc_10)/size}")
        
        print("Done!")
    
    def test_instr(self, subject, feature_csv):
        bug_id = feature_csv.name.split(".")[0]
        buggy_line_key = self.get_buggy_line_key(subject, bug_id)

        # 1. Dataset Making
        test_dataset = FL_Dataset("test", [(subject, feature_csv)])

        # 2. DataLoader Making
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)

        # 3. Testing
        avg_test_loss, line_susp = self.test_on_model(test_loader)

        # 4. write line_susp to csv
        # key: susp. score
        self.write_line_susp_scores(line_susp, subject, bug_id)

        # 5. get rank of buggy function
        function_susp = self.get_function_level_results(line_susp, buggy_line_key)

        # 6. write function_susp to csv
        # [function_name, {susp.: susp. score, rank: rank}]
        self.write_function_susp_scores(function_susp, subject, bug_id)

        # 7. get rank of buggy function
        rank = self.get_rank_of_buggy_function(function_susp, buggy_line_key)

        return rank
    
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
    
    def get_function_level_results(self, key_susp, buggy_line_key):
        buggy_target_file = buggy_line_key.split("#")[0].split("/")[-1]
        buggy_function_name = buggy_line_key.split("#")[1]
        buggy_lineno = int(buggy_line_key.split("#")[-1])

        # make dict that contains function as key
        # and the highest susp. score from the lines in the function
        function_susp = {}
        for key, susp in key_susp.items():
            target_file = key.split("#")[0].split("/")[-1]
            function_name = key.split("#")[1]
            lineno = int(key.split("#")[-1])

            if function_name not in function_susp:
                function_susp[function_name] = {"susp.": susp}
            else:
                function_susp[function_name]["susp."] = max(function_susp[function_name]["susp."], susp)
        

        # sort function_susp by susp. score
        # I have to get with key as function name
        function_susp = sorted(function_susp.items(), key=lambda x: x[1]["susp."], reverse=True)

        # change function_susp to pandas dataframe
        # to get rank of buggy function
        function_susp = [(function_name, susp_dict["susp."]) for function_name, susp_dict in function_susp]
        function_susp = pd.DataFrame(function_susp, columns=["function", "susp."])
        function_susp = function_susp.sort_values(by="susp.", ascending=False).reset_index(drop=True)
        function_susp["rank"] = function_susp["susp."].rank(ascending=False, method="max").astype(int)

        # now change is back to (function_name, susp_dict{susp., rank}) format
        function_susp = [(function_name, {"susp.": susp, "rank": rank}) for function_name, susp, rank in zip(function_susp["function"], function_susp["susp."], function_susp["rank"])]

        return function_susp
    
    def get_buggy_line_key(self, subject, bug_id):
        bug_keys_dir = self.project_out_dir / "bug_keys"
        buggy_keys_csv = bug_keys_dir / f"{subject}-{bug_id}.buggy_line_key.txt"
        assert buggy_keys_csv.exists(), f"Error: {buggy_keys_csv} does not exist."
        with open(buggy_keys_csv, "r") as f:
            buggy_line_key = f.readline().strip()
        return buggy_line_key

    
    def write_line_susp_scores(self, line_susp, subject, bug_id):
        line_susp_csv = self.model_line_susp_score_dir / f"{subject}-{bug_id}.line_susp_score.csv"
        with open(line_susp_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "suspiciousness"])
            for key, susp in line_susp.items():
                writer.writerow([key, susp])
    
    def write_function_susp_scores(self, function_susp, subject, bug_id):
        function_susp_csv = self.model_function_susp_score_dir / f"{subject}-{bug_id}.function_susp_score.csv"
        with open(function_susp_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["function", "suspiciousness", "rank"])
            for function_name, susp_dict in function_susp:
                writer.writerow([function_name, susp_dict["susp."], susp_dict["rank"]])
    
    # ==============================
    # Testing Loop
    # ==============================
    def test_on_model(self, test_loader):
        self.mlp_model.eval()

        total_loss = 0.0
        total_test_loss = []

        line_susp = {}

        for i, (key, features, label) in enumerate(test_loader):
            # Load data to device
            features, label = features.to(self.device), label.to(self.device)

            # resize label
            label = label.view(-1, 1)

            # Forward pass
            y_hat = self.mlp_model(features)

            # Compute loss
            loss = self.loss_fn(y_hat, label)
            total_test_loss.append(loss.item())
            total_loss += loss.item()

            # Save key and suspiciousness for all key in batch
            for k, y in zip(key, y_hat):
                assert k not in line_susp, f"Error: {k} already exists."
                line_susp[k] = y.item()

        avg_test_loss = np.mean(total_test_loss)
        return avg_test_loss, line_susp




    # ==============================
    # Training Loop
    # ==============================
    def train_loop(self):
        size = len(self.train_loader.dataset)

        self.mlp_model.train()
        total_loss = 0.0
        total_train_loss = []

        for i, (key, features, label) in enumerate(self.train_loader):
            # Load data to device
            features, label = features.to(self.device), label.to(self.device)

            # resize label
            label = label.view(-1, 1)

            # Zero the gradients
            self.optimizer.zero_grad()

            # Forward pass
            y_hat = self.mlp_model(features)

            # Compute loss
            loss = self.loss_fn(y_hat, label)
            total_train_loss.append(loss.item())

            # Backward pass
            loss.backward()

            # Optimize
            self.optimizer.step()
            total_loss += loss.item()

            if i % 100 == 0:
                loss, current = loss.item(), i * len(features)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
        
        avg_train_loss = np.mean(total_train_loss)
        return avg_train_loss
    
    # ==============================
    # Validation Loop
    # ==============================
    def validate_loop(self):
        size = len(self.validate_loader.dataset)

        self.mlp_model.eval()
        total_loss = 0.0
        total_validate_loss = []

        for i, (key, features, label) in enumerate(self.validate_loader):
            # Load data to device
            features, label = features.to(self.device), label.to(self.device)

            # resize label
            label = label.view(-1, 1)
            
            # Forward pass
            y_hat = self.mlp_model(features)

            # Compute loss
            loss = self.loss_fn(y_hat, label)
            total_validate_loss.append(loss.item())
            total_loss += loss.item()

        avg_validate_loss = np.mean(total_validate_loss)
        print(f"Validation Error: \n Avg loss: {avg_validate_loss:>8f} \n")

        return avg_validate_loss


    # ==============================
    # Save Parameters
    # ==============================
    def save_parameters(self):
        config_param = {
            "project_name": self.project_name,
            "dataset_pair_list": self.dataset_pair_list,
            "train_ratio": self.train_ratio,
            "validate_ratio": self.validate_ratio,
            "test_ratio": self.test_ratio,
            "random_seed": self.random_seed
        }
        with open(self.project_out_dir / "config_param.json", "w") as f:
            json.dump(config_param, f, indent=4)
        print(f"config param:")
        print(json.dumps(config_param, indent=2))

        model_param = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "dropout": self.dropout,
            "stack_size": self.stack_size,
            "output_size": self.output_size
        }
        with open(self.project_out_dir / "model_param.json", "w") as f:
            json.dump(model_param, f, indent=4)
        print(f"model param:")
        print(json.dumps(model_param, indent=2))

        training_param = {
            "epoch": self.epoch,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "device": self.device
        }
        with open(self.project_out_dir / "training_param.json", "w") as f:
            json.dump(training_param, f, indent=4)
        print(f"training param:")
        print(json.dumps(training_param, indent=2))
        
        print(f"Saved parameters to {self.project_out_dir}")


    # ==============================
    # Dataset Splitting
    # ==============================
    def load_raw_dataset(self):
        raw_dataset = []
        
        for subject, dataset_name in self.dataset_pair_list:
            dataset_dir = out_dir / subject / dataset_name
            pp_fl_features_dir = dataset_dir / "PP_FL_features_per_bug_version"


            feature_csv_list = [f for f in pp_fl_features_dir.iterdir() if not f.is_dir()]
            feature_csv_list = sorted(feature_csv_list, key=lambda x: int(x.name.split(".")[0][3:]))

            for feature_csv in feature_csv_list:
                self.copy_buggy_keys(subject, dataset_dir, feature_csv)
                raw_dataset.append((subject, feature_csv))
            
        # shuffle raw_dataset
        random.shuffle(raw_dataset)

        return raw_dataset

    def copy_buggy_keys(self, subject, dataset_dir, feature_csv):
        bug_id = feature_csv.name.split(".")[0]
        buggy_line_key_txt = dataset_dir / "buggy_line_key_per_bug_version" / f"{bug_id}.buggy_line_key.txt"
        assert buggy_line_key_txt.exists(), f"Error: {buggy_line_key_txt} does not exist."
        
        bug_keys_dir = self.project_out_dir / "bug_keys"
        bug_keys_dir.mkdir(exist_ok=True, parents=True)

        buggy_keys_csv = bug_keys_dir / f"{subject}-{buggy_line_key_txt.name}"
        shutil.copy(buggy_line_key_txt, buggy_keys_csv)

    def split_dataset(self):
        total_size = len(self.raw_dataset)
        train_size = int(total_size * self.train_ratio / 10)
        validate_size = int(total_size * self.validate_ratio / 10)
        test_size = int(total_size * self.test_ratio / 10)

        self.raw_train_set = self.raw_dataset[:train_size]
        self.raw_validate_set = self.raw_dataset[train_size:train_size+validate_size]
        self.raw_test_set = self.raw_dataset[train_size+validate_size:]

        self.save_split_dataset()
    
    def save_split_dataset(self):
        split_dataset_dir = self.project_out_dir / "split_dataset"
        split_dataset_dir.mkdir(exist_ok=True, parents=True)

        self.save_split_dataset_set(self.raw_train_set, split_dataset_dir, "train")
        self.save_split_dataset_set(self.raw_validate_set, split_dataset_dir, "validate")
        self.save_split_dataset_set(self.raw_test_set, split_dataset_dir, "test")

    def save_split_dataset_set(self, dataset_set, split_dataset_dir, set_name):
        dataset_set_dir = split_dataset_dir / set_name
        dataset_set_dir.mkdir(exist_ok=True, parents=True)

        for subject, feature_csv in dataset_set:
            bug_id = feature_csv.name.split(".")[0]

            feature_csv_name = f"{subject}-{feature_csv.name}"
            shutil.copy(feature_csv, dataset_set_dir / feature_csv_name)
