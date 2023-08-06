"""Calculating word frequencies in corpora."""
import numpy as np


def freqs(counts, n):
    keys = counts.keys()
    tok_counts = np.array(list(counts.values()))
    freqs = tok_counts / n
    return dict(zip(keys, freqs))
