"""Small deep MLP shared by training and inference."""
import torch.nn as nn


class RiskMLP(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(n_features, 64), nn.ReLU(), nn.Dropout(0.15),
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.10),
            nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, inputs):
        return self.layers(inputs).squeeze(-1)
