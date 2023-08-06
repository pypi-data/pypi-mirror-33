from w2v import preprocessing, datasets


def default_config(name):
    """Get a default config.

    Args:
      name: String, a name for the dataset.

    Returns:
      Dictionary.
    """
    return {'tokenizer': 'spacy',
            'reader': 'window',
            'name': name,
            'k': 5,
            't': 1e-5}


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
