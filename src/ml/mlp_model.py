import torch
import torch.nn as nn

class MLP_Model(nn.Module):
    def __init__(
            self,
            model_shape, # 2024-08-08
            dropout,
    ):
        super(MLP_Model, self).__init__()
        self.fc_list = [] # 2024-08-08
        for i in range(len(model_shape)-1):
            fc = nn.Linear(model_shape[i], model_shape[i+1])
            # norm = nn.BatchNorm1d(model_shape[i+1])
            relu = nn.ReLU()
            dp = nn.Dropout(dropout)
            # self.fc_list.extend([fc, norm, dp])
            self.fc_list.extend([fc, relu, dp])
        self.fc_list.pop()
        self.fc_list.pop()

        self.fc_list = nn.ModuleList(self.fc_list)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        out = x
        for fc in self.fc_list:
            out = fc(out)
        out = self.sigmoid(out)
        return out
