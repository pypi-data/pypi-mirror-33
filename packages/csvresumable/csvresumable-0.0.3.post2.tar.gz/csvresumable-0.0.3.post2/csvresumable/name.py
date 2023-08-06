import os.path
import sys
import hashlib
from .consts import CACHE_DIR


def get_identity(
    argv=None,
    prefix=CACHE_DIR if CACHE_DIR.endswith("/") else CACHE_DIR + "/",
    suffix=".csv",
    encoding="utf-8",
    hasher=hashlib.sha1,
    extra=None,
):
    """
    get_identity('main')
    '~/.cache/py-resumable/b28b7af69320201d1cf206ebf28373980add1451.csv'
    """
    if argv is None:
        argv = sys.argv[:]
    if not isinstance(argv, (str, bytes)):
        if len(argv) > 0:
            argv[0] = os.path.abspath(argv[0])
        if extra is not None:
            argv = [argv[0], extra]
        argv = "@".join(argv)
    if not isinstance(argv, bytes):
        argv = argv.encode(encoding)
    hash_value = hasher(argv)
    identity = "{}{}{}".format(prefix, hash_value.hexdigest(), suffix)
    return identity


def with_decoration(filepath, *, prefix):
    """
    >>> with_decoration('./foo/bar.txt', prefix='super-')
    './foo/super-bar.txt'
    """
    d = os.path.dirname(filepath)
    b, ext = os.path.splitext(os.path.basename(filepath))
    return os.path.join(d, "{}{}{}".format(prefix, b, ext))
