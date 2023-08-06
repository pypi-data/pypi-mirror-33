"""For creating and managing vocabularies."""


# Defaults for
SOS = '<S>'
EOS = '</S>'
PAD = "<PAD>"
UNK = "<UNK>"
# LBR and RBR are for handling S-Expressions, though usage is fairly obscure
LBR = '('
RBR = ')'


def extra_tokens():
    """Get a list of extra tokens added to Vocab.

    Returns:
      List of strings.
    """
    return [SOS, EOS, PAD, UNK, LBR, RBR]


class Vocab:
    """Wrapper for a vocab dict.

    Exposes indexing for both strings and integers for forward and reverse
    lookup.

    Examples:
      word_id = vocab['word']
      word = vocab[word_id]

    Attributes:
      name: String.
      ix: Dictionary, mapping word keys to index values {token: id}.
      word: Dictionary, mapping index keys to word values {id: token}.
      n: Integer, the number of words in the vocabulary.
      pad: String, the padding token. Default is "<PAD>".
      unk: String, the unknown token.
      sos: String, the start of sequence token. Default is "<S>".
      eos: String, the end of sequence token. Default is "</S>".
      pad_ix: Integer, the index of the pad token.
      unk_ix: Integer, the index of the unknown token.
      sos_ix: Integer, the index of the sos token.
      eos_ix: Integer, the index of the eos token.
    """

    def __init__(self, name, words, pad=PAD, unk=UNK, sos=SOS, eos=EOS):
        """Create a new Vocab.

        Args:
          name: String, the name of the vocabulary, e.g. the dataset name.
          words: Set of strings.
          pad: String, the padding token. Default is global PAD.
          unk: String, the unknown token. Default is global UNK.
          sos: String, the start of sequence token. Default is global SOS.
          eos: String, the end of sequence token. Default is global EOS.
        """
        self.name = name
        words.update([sos, eos, pad, unk, LBR, RBR])
        self.ix = dict(zip(words, range(1, len(words) + 1)))
        # Make sure PAD is ix 0
        self.ix[pad] = 0
        self.word = {v: k for k, v in self.ix.items()}
        self.n = len(self.ix)
        self.pad = pad
        self.unk = unk
        self.sos = sos
        self.eos = eos
        self.pad_ix = self[pad]
        self.unk_ix = self[unk]
        self.sos_ix = self[sos]
        self.eos_ix = self[eos]

    def __getitem__(self, item):
        # Item may be either an int or a string (forward or reverse lookup)
        if isinstance(item, int):
            return self.word[item]
        elif isinstance(item, str):
            return self.ix[item]
        else:
            raise ValueError('Unexpected type: %s.' % type(item))

    def __len__(self):
        return self.n

    def __repr__(self):
        return 'Vocab for %s with %s words.' % (self.name, self.n)
