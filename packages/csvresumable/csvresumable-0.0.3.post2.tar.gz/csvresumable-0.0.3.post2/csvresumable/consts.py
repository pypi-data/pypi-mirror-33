import os.path

RESUME_DEFAULT = bool(os.environ.get("RESUME", ""))
CACHE_DIR = os.environ.get("RESUMABLE_CACHEDIR", ""
                           ) or os.path.join(os.path.expanduser("~"), ".cache/py-resumable")
TMP_DIR = os.path.join(CACHE_DIR, "tmp")
