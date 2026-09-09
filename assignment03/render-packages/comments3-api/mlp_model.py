# -*- coding: utf-8 -*-
"""Shared PyTorch MLP definition — must mirror the notebook architecture exactly."""
import torch
import torch.nn as nn


class MLP(nn.Module):
    """3-class MLP (logits output) theo notebook App 3."""

    def __init__(self, input_dim, hidden=(64, 32), n_classes=3):
        super().__init__()
        layers, prev = [], input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, n_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
