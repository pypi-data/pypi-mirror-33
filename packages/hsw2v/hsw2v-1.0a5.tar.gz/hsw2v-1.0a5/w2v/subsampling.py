"""Subsampling frequent words."""
import numpy as np


def p(freqs, t=0.0001):
    """Get probabilities for sampling a word based on frequencies.

    .. math::
      P(w_i) = 1 - \sqrt{\frac{t}{f(w_i)}}

    Note on t:
      "...this subsampling formula...aggressively subsamples words whose
      frequency is greater than t..."
    https://arxiv.org/pdf/1310.4546.pdf

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
