from functools import wraps
from operator import itemgetter
from signal import getsignal, signal, SIGPIPE, SIG_DFL


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


def suppress_sigpipe(f):
    """Decorator to handle SIGPIPE cleanly.

    Prevent Python from turning SIGPIPE into an exception and printing an
    uncatchable error message. Note, if the wrapped function depends on the
    default behavior of Python when handling SIGPIPE this decorator may have
    unintended effects."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        orig_handler = getsignal(SIGPIPE)
        signal(SIGPIPE, SIG_DFL)
        try:
            f(*args, **kwargs)
        finally:
            signal(SIGPIPE, orig_handler)  # restore original Python SIGPIPE handler
    return wrapper
