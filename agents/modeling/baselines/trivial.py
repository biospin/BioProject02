"""
Three trivial baselines required by the 7-point Critic checklist (item 2).

- RandomBaseline     : predict positive with fixed probability
- MajorityBaseline   : always predict the majority class from train set
- MeanEmbedBaseline  : logistic regression on mean-pooled tile embedding
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score


class RandomBaseline:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        self.pos_rate = 0.5

    def fit(self, X: list[np.ndarray], y: np.ndarray):
        self.pos_rate = y.mean()

    def predict_proba(self, X: list[np.ndarray]) -> np.ndarray:
        return self.rng.uniform(0, 1, len(X)).astype(np.float32)


class MajorityBaseline:
    def __init__(self):
        self.majority_prob = 0.5

    def fit(self, X: list[np.ndarray], y: np.ndarray):
        self.majority_prob = float(y.mean() >= 0.5)

    def predict_proba(self, X: list[np.ndarray]) -> np.ndarray:
        return np.full(len(X), self.majority_prob, dtype=np.float32)


class MeanEmbedBaseline:
    """Logistic regression on mean-pooled tile embeddings (pixel-mean proxy)."""

    def __init__(self, seed: int = 42):
        self.clf = LogisticRegression(max_iter=1000, random_state=seed)

    def _pool(self, X: list[np.ndarray]) -> np.ndarray:
        return np.stack([x.mean(axis=0) for x in X])

    def fit(self, X: list[np.ndarray], y: np.ndarray):
        self.clf.fit(self._pool(X), y)

    def predict_proba(self, X: list[np.ndarray]) -> np.ndarray:
        return self.clf.predict_proba(self._pool(X))[:, 1].astype(np.float32)


def evaluate(name: str, proba: np.ndarray, y: np.ndarray) -> dict:
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "baseline": name,
        "auc": round(float(roc_auc_score(y, proba)), 4) if len(np.unique(y)) > 1 else None,
        "auprc": round(float(average_precision_score(y, proba)), 4) if len(np.unique(y)) > 1 else None,
        "balanced_accuracy": round(float(balanced_accuracy_score(y, preds)), 4),
        "n": len(y),
    }
    return metrics
