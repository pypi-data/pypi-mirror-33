"""Reading contexts from data."""


def get_reader(name, config):
    if name == 'window':
        return WindowReader(config['k'])
    else:
        raise ValueError('Unexpected reader name "%r"' % name)


class Context:
    """Interface declaration and base implementation.

    Attributes:
      x: object, the center object (e.g. token).
      context: set.
    """

    def __init__(self, x):
        self.x = x
        self.context = set([])

    def __iter__(self):
        for x in self.context:
            yield x

    def __len__(self):
        return len(self.context)

    def __repr__(self):
        return 'x: %s\ncontext: %s' % (self.x, ' '.join(self.context))

    def update(self, context):
        """Update this context.

        Args:
          context: List of objects in the context.
        """
        context = [c for c in context if c != self.x]
        self.context.update(context)


class Reader:
    """Interface declaration."""

    def __call__(self, inputs, *args):
        return self.contexts_and_pairs(inputs)

    def contexts_and_pairs(self, inputs):
        raise NotImplementedError


class WindowReader(Reader):
    """Read a context window around tokens in text."""

    def __init__(self, k):
        """Create a new WindowReader.

        Args:
          k: Integer, window size.
        """
        self.k = k

    def contexts_and_pairs(self, tokens):
        contexts = {}
        pairs = []
        for i, token in enumerate(tokens):
            context = self.token_context(i, tokens)
            if token not in contexts.keys():
                contexts[token] = Context(token)
            contexts[token].update(context)
            pairs += list(zip([token] * len(context), context))
        return contexts, pairs

    def token_context(self, center_ix, tokens):
        """Get left and right contexts for the token.

        Args:
          center_ix: Integer.
          tokens: List of strings.

        Returns:
          contexts: Dictionary.
        """
        left_start = max(0, center_ix - self.k)
        left_end = center_ix
        left_context = tokens[left_start:left_end]
        right_start = center_ix + 1
        right_end = min(len(tokens), center_ix + 1 + self.k)
        right_context = tokens[right_start:right_end]
        return left_context + right_context
