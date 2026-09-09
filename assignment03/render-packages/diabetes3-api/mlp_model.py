# -*- coding: utf-8 -*-
"""Shared PyTorch MLP definition — must mirror the notebook architecture exactly.

Load: m = MLP(input_dim, hidden, num_classes); m.load_state_dict(torch.load(path)).
"""
import torch
import torch.nn as nn


class MLP(nn.Module):
    """MLP theo Slide 03 trang 19 — trả về logits (không sigmoid/softmax trong model)."""

    def __init__(self, input_dim, hidden=(64, 32), num_classes=1):
        super().__init__()
        layers, prev = [], input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
