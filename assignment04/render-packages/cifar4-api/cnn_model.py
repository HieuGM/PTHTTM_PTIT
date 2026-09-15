# -*- coding: utf-8 -*-
"""Shared PyTorch CNN definitions — must mirror the notebook 02 (M4 SE-CNN) exactly."""
import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    """y = ReLU(BN(Conv(ReLU(BN(Conv(x)))))) + x — giống notebook 02 §6."""

    def __init__(self, ch):
        super().__init__()
        self.conv1 = nn.Conv2d(ch, ch, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(ch)
        self.conv2 = nn.Conv2d(ch, ch, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(ch)

    def forward(self, x):
        identity = x
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return torch.relu(out + identity)


class SEBlock(nn.Module):
    """Squeeze-and-Excitation channel attention — giống notebook 02 §6."""

    def __init__(self, ch, reduction=4):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(ch, max(ch // reduction, 1)), nn.ReLU(),
            nn.Linear(max(ch // reduction, 1), ch), nn.Sigmoid(),
        )

    def forward(self, x):
        b, c, _, _ = x.shape
        s = self.fc(self.pool(x).view(b, c)).view(b, c, 1, 1)
        return x * s


class SEClassifier(nn.Module):
    """M4 (tutorial §45): Conv+BN blocks + Residual + SE attention → GAP → Dense."""

    def __init__(self, num_classes=10):
        super().__init__()
        ch = 32

        def block(cin, cout):
            layers = [nn.Conv2d(cin, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(),
                      nn.Conv2d(cout, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU()]
            return nn.Sequential(*layers)

        self.b1 = block(3, ch)
        self.b2 = block(ch, ch * 2)
        self.res = ResidualBlock(ch * 2)
        self.se = SEBlock(ch * 2)
        self.pool = nn.MaxPool2d(2)
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(ch * 2, num_classes)

    def forward(self, x):
        x = self.pool(self.b1(x))
        x = self.pool(self.b2(x))
        x = self.se(self.res(x))
        return self.fc(self.gap(x).flatten(1))

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
