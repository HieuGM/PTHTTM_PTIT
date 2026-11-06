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


class TwoLayerMLP(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(n_features, 64), nn.ReLU(), nn.Dropout(.15),
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(.10), nn.Linear(32, 1))

    def forward(self, inputs):
        return self.layers(inputs).squeeze(-1)


class ResidualBlock(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.transform = nn.Sequential(nn.Linear(width, width), nn.ReLU(), nn.Dropout(.10),
                                       nn.Linear(width, width))
        self.activation = nn.ReLU()

    def forward(self, inputs):
        return self.activation(inputs + self.transform(inputs))


class ResidualMLP(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.input = nn.Sequential(nn.Linear(n_features, 32), nn.ReLU())
        self.blocks = nn.Sequential(ResidualBlock(32), ResidualBlock(32))
        self.output = nn.Linear(32, 1)

    def forward(self, inputs):
        return self.output(self.blocks(self.input(inputs))).squeeze(-1)


def build_model(n_features, model_id='mlp3'):
    classes = {'mlp2': TwoLayerMLP, 'mlp3': RiskMLP, 'resmlp': ResidualMLP}
    if model_id not in classes:
        raise ValueError(f'Unknown neural architecture: {model_id}')
    return classes[model_id](n_features)
