from logging import getLogger as get_logger
import atexit
import os.path
import csv
import tempfile
from .langhelpers import reify
from .name import get_identity
from .consts import TMP_DIR

logger = get_logger(__name__)


class Recorder:
    writer_factory = csv.writer

    def __init__(self, *, name=None, extra=None, dir=TMP_DIR, register=atexit.register):
        self.name = name or get_identity(extra=extra)
        self.register = register
        self.dir = dir
        self._wf = None

    @reify
    def writer(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir, exist_ok=True)
        self._wf = tempfile.NamedTemporaryFile("w", delete=False, dir=self.dir)
        logger.debug("create temporary file %s", self._wf.name)
        self.register(self.finalize)
        return self.writer_factory(self._wf)

    def record(self, row):
        self.writer.writerow(row)

    def finalize(self):
        if self._wf is None:
            return
        self._wf.close()
        dirpath = os.path.dirname(self.name)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        logger.debug("rename file %s -> %s", self._wf.name, self.name)
        os.rename(self._wf.name, self.name)
