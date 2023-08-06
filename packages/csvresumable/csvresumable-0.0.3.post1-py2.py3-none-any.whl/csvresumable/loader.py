import os
import csv
import itertools
from logging import getLogger as get_logger
from .consts import RESUME_DEFAULT
logger = get_logger(__name__)


class Loader:
    reader_factory = csv.reader

    def __init__(self, iterator, recorder, *, key, resume=None):
        self.key = key
        self.iterator = iterator
        self.recorder = recorder
        self.need_resume = resume or RESUME_DEFAULT

    def __iter__(self):
        rows = []
        if self.need_resume:
            if os.path.exists(self.recorder.name):
                with open(self.recorder.name) as rf:
                    try:
                        for used_row in self.reader_factory(rf):
                            rows.append(next(self.iterator))
                            k = self.key(rows[-1])
                            if k != used_row[0]:
                                break
                            rows.pop()
                            logger.debug("skip %r (already used)", k)
                            self.recorder.record([k])
                    except StopIteration:
                        pass

        for row in itertools.chain(rows, self.iterator):
            retval = yield row
            if retval is None:
                self.recorder.record([self.key(row)])
