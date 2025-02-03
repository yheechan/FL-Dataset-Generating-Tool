from torch.utils.data import Dataset
import csv
import numpy as np
import torch

from lib.susp_score_formula import *

class FL_Dataset(Dataset):
    def __init__(self, name, raw_data_list):
        self.name = name
        self.raw_data_list = raw_data_list
        fl_features = ["ep", "ef", "np", "nf"]
        for sbfl_form, sub_form_list in final_sbfl_formulas.items():
            fl_features.extend(sub_form_list)
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            fl_features.extend(sub_form_list)
        self.feature_names = fl_features
        self.data_list = self.make_data_list()
    
    def __len__(self):
        return len(self.data_list)
    
    def __getitem__(self, idx):
        key, features, label, line_key = self.data_list[idx]
        return key, features, label, line_key

    def make_data_list(self):
        data_list = []
        for bug_idx, lines_data_list in self.raw_data_list.items():
            data = self.load_data(bug_idx, lines_data_list)
            data_list.extend(data)
        return data_list

    def load_data(self, bug_idx, lines_data_list):
        data = []
        bug = 0
        nonBug = 0

        for line_features in lines_data_list:
            key = bug_idx
            features = [float(line_features[form]) for form in self.feature_names]
            features = torch.tensor(np.array(features), dtype=torch.float32)
            if line_features["is_buggy_line"] == "True":
                bug += 1
            else:
                nonBug += 1

            label_val = 1 if line_features["is_buggy_line"] == "True" else 0
            label = torch.tensor(np.array(label_val), dtype=torch.float32)

            file = line_features["file"]
            function = line_features["function"]
            lineno = line_features["lineno"]
            line_key = f"{file}#{function}#{lineno}"
        
            data.append((key, features, label, line_key))
        
        assert bug == 1, f"Bug: {bug}, NonBug: {nonBug}"

        weight_bug = (bug + nonBug) / (bug * 2)
        weight_nonBug = (bug + nonBug) / (nonBug * 2)        
        self.weight = [weight_nonBug, weight_bug]
        # pos_weight is the number how many more negative samples than positive samples
        self.pos_weight = weight_bug / 64
        self.pos_weight = weight_bug

        return data
