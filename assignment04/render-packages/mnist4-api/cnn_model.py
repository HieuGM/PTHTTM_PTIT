# -*- coding: utf-8 -*-
"""Shared PyTorch CNN definition — must mirror the notebook architecture exactly.

Load: m = TorchCNN(); m.load_state_dict(torch.load(path)); m.eval()
"""
import torch
import torch.nn as nn


class TorchCNN(nn.Module):
    """CNN 1→8→16 kênh + MaxPool + Dense — giống hệt NumPyCNN trong notebook 01."""

    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3), nn.ReLU(),
            nn.Conv2d(8, 16, kernel_size=3), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
        )
        self.classifier = nn.Linear(16 * 12 * 12, num_classes)

    def forward(self, x):
        return self.classifier(self.features(x))

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
