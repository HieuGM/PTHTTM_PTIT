# -*- coding: utf-8 -*-
"""Shared PyTorch MLP definition — must mirror the notebook architecture exactly."""
import torch
import torch.nn as nn


class MLP(nn.Module):
    """Regression MLP (linear output head) theo notebook App 2."""

    def __init__(self, input_dim, hidden=(64, 32)):
        super().__init__()
        layers, prev = [], input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
