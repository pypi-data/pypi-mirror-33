"""Data structures for inputs."""


class IterableAdapter:
    """Wrapper for reusing iterables.

    https://stackoverflow.com/questions/1271320/
    resetting-generator-object-in-python

    michaelsnowden's answer.
    """

    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __iter__(self):
        return self.iterator_factory()
