class DictList(list):
    """
    A util to check if list of dictionaries has a subdictionary.

    Example:
    >>> d = DictList([
        {'name': 'cool', 'a': 1, 'x': 0},
        {'name': 'nice', 'b': 2, 'y': 0}
    ])
    >>> d.exists({'name': 'cool', 'a': 1})
    True
    >>> d.exists({'name': 'bool'})
    False
    """
    def exists(self, subdict):
        for i, item in enumerate(self):

            true_count = 0
            for k, v in enumerate(subdict):
                if item.get(v) == subdict.get(v):
                    true_count += 1

            if true_count == len(subdict):
                return True

        return False
