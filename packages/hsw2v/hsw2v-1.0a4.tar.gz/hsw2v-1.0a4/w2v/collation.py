"""Collate functions."""


class Collate:
    """Callable collate function."""

    def __init__(self, neg_sampler):
        """Create a new Collate.

        Args:
          neg_sampler: w2v.neg_sampling.NegativeSampler.
        """
        self.sampler = neg_sampler

    def __call__(self, pairs):
        """Call the collate function.

        Args:
          pairs: List of tuples of strings (center, context).

        Returns:
          centers: List of strings.
          contexts: List of strings.
          negs: List of lists of strings.
        """
        batch_size = len(pairs)
        centers = [x[0] for x in pairs]
        contexts = [x[1] for x in pairs]
        negs = []
        for i in range(batch_size):
            negs.append(self.sampler(centers[i]))
        # a generic return type for base class (can override with specifics)
        return centers, contexts, negs
