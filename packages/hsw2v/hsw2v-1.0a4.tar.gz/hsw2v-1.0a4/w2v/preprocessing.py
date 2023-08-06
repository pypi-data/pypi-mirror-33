from w2v import frequencies, subsampling, tokenization, vocabulary, readers
import collections
import numpy as np


def preprocess(data, config):
    """Pre-process a dataset.

    Args:
      data: reusable iterator or list.
      config: Dictionary.

    Returns:
      vocab: w2v.vocabulary.Vocab.
      freqs: Dictionary.
      contexts: Dictionary.
      pairs: List of tuples.
      stats: Dictionary.
    """
    print('Preprocessing with config:')
    for key, value in config.items():
        print('\t%s\t%s' % (key, value))

    tokenizer = tokenization.get_tokenizer(config['tokenizer'])
    reader = readers.get_reader(config['reader'], config)

    word_set = set([])
    counts = collections.Counter()
    n = 0

    # first pass
    print('First pass...')
    for line in data:
        tokens = tokenizer(line)
        n += len(tokens)
        word_set.update(tokens)
        counts.update(tokens)

    vocab = vocabulary.Vocab(config['name'], word_set)
    freqs = frequencies.freqs(counts, n)
    for token in vocabulary.extra_tokens():
        freqs[token] = 1e-6  # this may be an issue in future if mapping to UNK
    drop_probs = subsampling.p(freqs, config['t'])
    subsampler = subsampling.SubSampler(drop_probs)
    contexts = {}
    pairs = []

    # second pass
    print('Second pass...')
    for line in data:
        tokens = tokenizer(line)
        tokens = subsampler(tokens)
        new_contexts, new_pairs = reader(tokens)
        # update contexts
        for token, context in new_contexts.items():
            if token not in contexts.keys():
                contexts[token] = readers.Context(token)
            contexts[token].update(context)
        pairs += new_pairs

    # gather and report stats
    context_lens = [len(c) for c in contexts.values()]
    avg_context_len = np.average(context_lens)
    stats = {
        'corpus_len': n,
        'vocab_size': len(vocab),
        'training_pairs': len(pairs),
        'avg_context_len': avg_context_len}
    print('Pre-processing complete.')
    print('Corpus length: %s' % n)
    print('Vocab size: %s' % len(vocab))
    print('Training pairs: %s' % len(pairs))
    print('Average context size: %s' % avg_context_len)

    return vocab, freqs, contexts, pairs, stats
