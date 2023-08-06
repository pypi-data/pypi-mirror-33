"""Wrappers for word2vec data."""
from torch.utils.data import dataset


class W2VDataset(dataset.Dataset):
    """Base W2V dataset.

    Attributes:
      vocab: w2v.vocabulary.Vocab.
      freqs: Dictionary.
      contexts: Dictionary.
      pairs: List of tuples.
    """

    def __init__(self, config, vocab, freqs, contexts, pairs):
        """Create a new W2VDataset.

        Args:
          config: Dictionary.
          vocab: w2v.vocabulary.Vocab.
          freqs: Dictionary.
          contexts: Dictionary.
          pairs: List of tuples.
        """
        for key, value in config.items():
            setattr(self, key, value)
        self.vocab = vocab
        self.freqs = freqs
        self.contexts = contexts
        self.pairs = pairs
        self._length = len(pairs)

    def __getitem__(self, i):
        return self.pairs[i]

    def __len__(self):
        return self._length
