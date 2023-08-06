try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2 backport


def makedirs(path, exist_ok=False):
    Path(path).mkdir(parents=True, exist_ok=exist_ok)
