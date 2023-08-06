from w2v import preprocessing, datasets


def dataset(data, config):
    """Get a dataset.

    Args:
      data: list or reusable iterable.
      config: Dictionary.

    Returns:
      w2v.datasets.W2VDataset.
    """
    vocab, freqs, contexts, pairs, _ = preprocessing.preprocess(data, config)
    return datasets.W2VDataset(config, vocab, freqs, contexts, pairs)
