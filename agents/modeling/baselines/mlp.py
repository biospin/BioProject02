"""
Slide-level MLP baseline for binary phenotype prediction.

Input:  (N, D) tile embeddings  →  mean-pooled to (1, D) slide vector
Output: binary label probability (e.g. ER+/-)
"""

import torch
import torch.nn as nn


class SlideMLP(nn.Module):
    def __init__(self, input_dim: int = 1024, hidden_dims: list = [512, 256], dropout: float = 0.3, num_classes: int = 1):
        super().__init__()
        layers = []
        in_dim = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(in_dim, h), nn.ReLU(), nn.Dropout(dropout)]
            in_dim = h
        layers.append(nn.Linear(in_dim, num_classes))
        self.net = nn.Sequential(*layers)
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (N, D) tile embeddings → logit(s)"""
        slide_vec = x.mean(dim=0, keepdim=True)   # (1, D)
        out = self.net(slide_vec).squeeze(0)       # (num_classes,) or scalar
        return out
