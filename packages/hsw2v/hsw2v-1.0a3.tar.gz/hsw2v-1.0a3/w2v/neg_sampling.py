"""Negative sampling."""
import numpy as np


class NegativeSampler:

    def __init__(self, frequencies, contexts, num_negs):
        """Create a new NegativeSampler.

        Args:
          frequencies: List of integers, the frequencies of each word,
            sorted in word index order.
          contexts: Dictionary.
          num_negs: Integer, how many to negatives to sample.
        """
        self.n = len(frequencies)
        self.values = list(frequencies.keys())
        self.contexts = contexts
        self.num_negs = num_negs
        self.distribution = self.p(list(frequencies.values()))

    def __call__(self, input):
        """Get negative samples.

        Args:
          input: object, e.g. a string or an integer ix.

        Returns:
          List of objects not in the context.
        """
        context = self.contexts[input]
        max_negs = self.n - len(context) - 1
        k = min(self.num_negs, max_negs)
        neg_ixs = np.random.choice(
            self.n,
            size=k,
            p=self.distribution,
            replace=False)
        negs = [self.values[ix] for ix in neg_ixs]
        # make sure we haven't sampled center word or its context
        invalid = [input] + list(context)
        for i, neg in enumerate(negs):
            while negs[i] in invalid:
                new_ix = np.random.choice(self.n,
                                          size=1,
                                          p=self.distribution)[0]
                new_neg = self.values[new_ix]
                if new_neg not in negs:
                    negs[i] = new_neg
        return negs

    def p(self, freqs):
        """Determine the probability distribution for negative sampling.

        Args:
          freqs: List of integers.

        Returns:
          numpy.ndarray.
        """
        freqs = np.array(freqs)
        return np.power(freqs, 3/4) / np.sum(np.power(freqs, 3/4))
