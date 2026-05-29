"""
Slide-level MLP baseline for binary phenotype prediction.

Input:  (N, D) tile embeddings  →  mean-pooled to (1, D) slide vector
Output: binary label probability (e.g. ER+/-)
"""

import torch
import torch.nn as nn


class SlideMLP(nn.Module):
    def __init__(self, input_dim: int = 1024, hidden_dims: list = [512, 256], dropout: float = 0.3):
        super().__init__()
        layers = []
        in_dim = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(in_dim, h), nn.ReLU(), nn.Dropout(dropout)]
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (N, D) tile embeddings → scalar logit"""
        slide_vec = x.mean(dim=0, keepdim=True)  # (1, D) mean pooling
        return self.net(slide_vec).squeeze(-1)    # (1,)
