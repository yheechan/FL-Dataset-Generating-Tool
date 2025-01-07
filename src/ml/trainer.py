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
from ml.engine_base import EngineBase

from lib.experiment import Experiment
from lib.database import CRUD
from lib.susp_score_formula import *

class Trainer(EngineBase):
    def __init__(self, 
                 # config param
                 subject_name, experiment_name,
                 train_ratio, validate_ratio, test_ratio,
                 random_seed=42,
                 # training param
                 epoch=3, batch_size=64, learning_rate=1e-3, device="cpu",
                 # model param
                 model_shape=[35, 512, 1024, 2048, 1024, 512, 1], # 2024-08-08
                 dropout=0.2,
    ):
        super().__init__()

        self.params = {
            "config_param": {
                "subject_name": subject_name,
                "experiment_name": experiment_name,
                "train_ratio": train_ratio,
                "validate_ratio": validate_ratio,
                "test_ratio": test_ratio,
                "random_seed": random_seed
            },
            "model_param": {
                "model_shape": model_shape, # 2024-08-08
                "dropout": dropout
            },
            "training_param": {
                "epoch": epoch,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "device": device
            }
        }
        
        # set random seed
        self.set_random_seed(self.params["config_param"]["random_seed"])

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
        # 0. Save Parameter as json
        self.write_parameter_file(self.project_out_dir, self.params)

        # 1. Dataset Splitting
        self.raw_dataset = self.load_raw_dataset(
            self.params["config_param"]["dataset_pair_list"],
            self.bug_keys_dir
        )
        self.raw_train_set, \
        self.raw_val_set, \
        self.raw_test_set = self.split_dataset(
            self.project_out_dir,
            self.raw_dataset,
            self.params["config_param"]["train_ratio"],
            self.params["config_param"]["validate_ratio"],
            self.params["config_param"]["test_ratio"]
        )

        # 2. Dataset Making
        self.train_dataset = FL_Dataset("train", self.raw_train_set)
        self.validate_dataset = FL_Dataset("validate", self.raw_val_set)
        print(f"Made datasets: train({len(self.train_dataset)}), validate({len(self.validate_dataset)})")

        # 3. DataLoader Making
        self.train_loader = DataLoader(self.train_dataset, batch_size=self.params["training_param"]["batch_size"], shuffle=True)
        self.validate_loader = DataLoader(self.validate_dataset, batch_size=self.params["training_param"]["batch_size"], shuffle=False)
        print(f"Made loaders: train({len(self.train_loader)}), validate({len(self.validate_loader)})")

        # 4. Model Making
        self.mlp_model = self.load_model(self.params["model_param"])
        self.mlp_model.to(self.params["training_param"]["device"])
        print(f"Made model: {self.mlp_model}")
        
        # 5. loss and optimizer
        # self.loss_fn = nn.CrossEntropyLoss()
        print(f"weight: {self.train_dataset.weight}")
        pos_weight = torch.tensor(self.train_dataset.pos_weight).to(self.params["training_param"]["device"])
        self.loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        self.optimizer = torch.optim.SGD(self.mlp_model.parameters(), lr=self.params["training_param"]["learning_rate"])
        # self.optimizer = torch.optim.Adam(self.mlp_model.parameters(), lr=self.params["training_param"]["learning_rate"])

        # 6. Training
        self.start_training()

        # 7. Testing
        self.start_testing(
            self.project_name, self.project_out_dir,
            self.raw_test_set, self.mlp_model,
            "test-accuracy.csv", self.params,
            self.model_line_susp_score_dir,
            self.model_function_susp_score_dir, self.bug_keys_dir
        )

        # 8. Save Model
        self.save_model(self.project_out_dir, self.mlp_model, self.params["config_param"]["project_name"])

    def start_training(self):
        epoch_size = self.params["training_param"]["epoch"]
        print(f"[{self.project_name}] Training model for {epoch_size} epochs...")
        
        train_loss = []
        validate_loss = []

        for epoch in range(epoch_size):
            print(f"\nEpoch {epoch+1}/{epoch_size}")
            avg_train_loss = self.train_loop()
            avg_validate_loss = self.validate_loop()
            print(f"EPOCH {epoch+1} TRAIN LOSS: {avg_train_loss}, VALIDATE LOSS: {avg_validate_loss}")
            train_loss.append(avg_train_loss)
            validate_loss.append(avg_validate_loss)
        
        print("Done!")

        # Save loss graph and csv
        self.draw_loss_graph(self.project_out_dir, train_loss, validate_loss) # 2024-08-08
        self.write_loss_to_csv(self.project_out_dir, train_loss, validate_loss)


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
            features = features.to(self.params["training_param"]["device"])
            label = label.to(self.params["training_param"]["device"])

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
            features = features.to(self.params["training_param"]["device"])
            label = label.to(self.params["training_param"]["device"])

            # resize label
            label = label.view(-1, 1)
            
            # Forward pass
            y_hat = self.mlp_model(features)

            # Compute loss
            loss = self.loss_fn(y_hat, label)
            total_validate_loss.append(loss.item())
            total_loss += loss.item()

        avg_validate_loss = np.mean(total_validate_loss)

        return avg_validate_loss
