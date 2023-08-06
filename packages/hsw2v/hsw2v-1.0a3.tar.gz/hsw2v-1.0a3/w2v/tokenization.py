"""Tokenization functions."""
import nltk
import spacy


def get_tokenizer(name):
    if name == 'nltk':
        return NLTKTokenizer()
    elif name == 'spacy':
        return SpacyTokenizer()
    else:
        raise ValueError('Unexpected tokenizer name "%r"' % name)


class Tokenizer:
    """Tokenizer interface declaration."""

    def __call__(self, text):
        return self.tokenize(text)

    def tokenize(self, text):
        raise NotImplementedError


class NLTKTokenizer(Tokenizer):
    """NLTK tokenizer."""

    def __init__(self):
        super(NLTKTokenizer, self).__init__()

    def tokenize(self, text):
        return nltk.word_tokenize(text)


class SpacyTokenizer(Tokenizer):
    """Spacy tokenizer."""

    def __init__(self):
        super(SpacyTokenizer, self).__init__()
        self.nlp = spacy.load('en')

    def tokenize(self, text):
        doc = self.nlp(text)
        return [t.text for t in doc]
