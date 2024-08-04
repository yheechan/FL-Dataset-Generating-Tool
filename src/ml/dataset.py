from torch.utils.data import Dataset
import csv
import numpy as np
import torch

from lib.susp_score_formula import *

class FL_Dataset(Dataset):
    def __init__(self, name, raw_data_list):
        self.name = name
        self.raw_data_list = raw_data_list
        self.feature_names = pp_sbfl_formulas + ["metallaxis", "muse"]
        self.data_list = self.make_data_list()
    
    def __len__(self):
        return len(self.data_list)
    
    def __getitem__(self, idx):
        key, features, label = self.data_list[idx]
        return key, features, label

    def make_data_list(self):
        print(f"Making dataset: {self.name}")
        data_list = []
        for subject, feature_csv in self.raw_data_list:
            data = self.load_data(feature_csv)
            data_list.extend(data)
        return data_list

    def load_data(self, feature_csv):
        data = []
        bug = 0
        nonBug = 0
        with open(feature_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["key"]
                features = [float(row[form]) for form in self.feature_names]
                features = torch.tensor(np.array(features), dtype=torch.float32)
                if row["bug"] == "1":
                    bug += 1
                else:
                    nonBug += 1
                label = torch.tensor(np.array(int(row["bug"])), dtype=torch.float32)
        
                data.append((key, features, label))
        
        weight_bug = (bug + nonBug) / (bug * 2)
        weight_nonBug = (bug + nonBug) / (nonBug * 2)        
        self.weight = [weight_nonBug, weight_bug]
        # pos_weight is the number how many more negative samples than positive samples
        self.pos_weight = weight_bug / 64
        self.pos_weight = weight_bug

        return data
