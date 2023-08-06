import os
import sys
import tempfile
import contextlib
from logging import getLogger as get_logger
from .name import get_identity
from .consts import (
    RESUME_DEFAULT,
    TMP_DIR,
)

logger = get_logger(__name__)


class MultiWriter:
    def __init__(self, *outs):
        self.outs = outs

    def write(self, body):
        for out in self.outs:
            out.write(body)

    def flush(self):
        for out in self.outs:
            out.flush()

    def close(self):
        for out in self.outs:
            out.close()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.flush()
        self.close()


@contextlib.contextmanager
def capture(
    name=None, *, out=sys.stdout, resume=RESUME_DEFAULT, redirect_stdout=True, dir=TMP_DIR
):
    name = name or get_identity(suffix=".capture")
    try:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        tmpf = tempfile.NamedTemporaryFile("w", dir=dir, delete=False)
        with MultiWriter(tmpf, out) as mwf:
            if resume and os.path.exists(name):
                logger.debug("replay start %r", name)
                with open(name) as rf:
                    for line in rf:
                        mwf.write(line)
                mwf.flush()
                logger.debug("replay end")

            if redirect_stdout:
                with contextlib.redirect_stdout(mwf):
                    yield mwf
            else:
                yield mwf
    finally:
        os.rename(tmpf.name, name)
