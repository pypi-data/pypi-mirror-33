from operator import itemgetter

def dslice(x, indexes):
    """Slice with discontinuous indexes."""
    if not x or not indexes:
        return []
    subx = itemgetter(*indexes)(x)
    if len(indexes) == 1:
        return [subx]
    else:
        return list(subx)


def spaces(text):
    """Replace all whitespace with single spaces."""
    return ' '.join(text.split())
