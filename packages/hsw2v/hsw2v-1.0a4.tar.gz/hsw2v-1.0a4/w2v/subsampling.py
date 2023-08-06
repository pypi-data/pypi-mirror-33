"""Subsampling frequent words."""
import numpy as np


def p(freqs, t=0.0001):
    """Get probabilities for sampling a word based on frequencies.

    Args:
      freqs: collections.Counter.
      t: float, constant for the function.

    Returns:
      Dictionary.
    """
    keys = freqs.keys()
    probs = np.maximum(0., 1. - np.sqrt(t / np.array(list(freqs.values()))))
    return dict(zip(keys, probs))


class SubSampler:

    def __init__(self, probs):
        self.probs = probs

    def __call__(self, items):
        return [i for i in items
                if not np.random.binomial(n=1, p=self.probs[i])]
