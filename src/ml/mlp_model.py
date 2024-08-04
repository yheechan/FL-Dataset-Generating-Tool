import torch
import torch.nn as nn

class Linear_Model(nn.Module):
    def __init__(self, input_size, dropout, output_size):
        super(Linear_Model, self).__init__()
        self.fc = nn.Linear(input_size, output_size)
        self.dp = nn.Dropout(dropout)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out = self.fc(x)
        out = self.dp(out)
        out = self.relu(out)
        return out

class MLP_Model(nn.Module):
    def __init__(
            self,
            input_size,
            hidden_size,
            dropout,
            stack_size,
            output_size
    ):
        super(MLP_Model, self).__init__()
        self.in_fc = Linear_Model(input_size, dropout, hidden_size)

        self.stack_size = stack_size - 2
        self.fc_list = [Linear_Model(hidden_size, dropout, hidden_size) for _ in range(stack_size)]
        self.fc_list = nn.ModuleList(self.fc_list)

        self.out_fc = nn.Linear(hidden_size, output_size)

        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        out = self.in_fc(x)
        for fc in self.fc_list:
            out = fc(out)
        out = self.out_fc(out)
        out = self.sigmoid(out)
        return out
    