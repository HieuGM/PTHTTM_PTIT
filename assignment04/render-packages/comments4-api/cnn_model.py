# -*- coding: utf-8 -*-
"""Shared PyTorch TextCNN definition — must mirror the notebook 03 architecture exactly."""
import torch
import torch.nn as nn


class TorchTextCNN(nn.Module):
    """TextCNN: Embedding(V,32) → Conv1d(32→64,k=3) → ReLU → max-over-time → Dense(3)."""

    def __init__(self, V, d=32, F=64, K=3, C=3):
        super().__init__()
        self.emb = nn.Embedding(V, d, padding_idx=0)
        self.conv = nn.Conv1d(d, F, K)
        self.pool = nn.AdaptiveMaxPool1d(1)
        self.fc = nn.Linear(F, C)

    def forward(self, ids):
        x = self.emb(ids).transpose(1, 2)
        h = torch.relu(self.conv(x))
        return self.fc(self.pool(h).squeeze(-1))

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
