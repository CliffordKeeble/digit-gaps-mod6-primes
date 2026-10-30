"""What the scripts in this folder share: where files live, a log that is also
printed, the lead at an index, and the clean-tree check the figures refuse to
draw without."""

import datetime
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"  # committed: the inputs read as filed
WORK = HERE / "work"  # not committed: the arrays the scripts make
LOGS = HERE / "logs"  # committed: what each script printed
IMAGES = HERE.parent.parent / "docs" / "img"


class Log:
    """Prints, and writes the same lines to logs/<name>.log (LF line endings)."""

    def __init__(self, name):
        self.path = LOGS / f"{name}.log"
        self.file = None

    def __call__(self, text=""):
        print(text)
        self.file.write(text + "\n")
        self.file.flush()

    def __enter__(self):
        LOGS.mkdir(exist_ok=True)
        self.file = self.path.open("w", encoding="utf-8", newline="\n")
        return self

    def __exit__(self, *exception):
        self.file.close()


def require_file(path, how_to_make_it):
    """Stop with a message naming the file, rather than draw without it."""
    if not Path(path).exists():
        sys.exit(f"{Path(path).name} is missing: {how_to_make_it}")


def describe_longdouble():
    """The platform fact that decides how the log-sums behave."""
    info = np.finfo(np.longdouble)
    return f"np.longdouble: {info.bits}-bit storage, {info.nmant + 1}-bit mantissa"


def lead_at_index(L5, L7, index):
    """The lead at the 5-series' index-th landing: its count minus the
    (interpolated) count of the 7-series at the same product size."""
    landing = np.asarray(L5[index])
    below = np.clip(np.searchsorted(L7, landing, side="right") - 1, 0, len(L7) - 2)
    span = L7[below + 1] - L7[below]
    return (np.asarray(index) + 1) - ((below + 1) + (landing - L7[below]) / span)


def source_state():
    """(short commit, date) of the scripts and data drawing a figure.

    Refuses a dirty tree: anything under this folder, other than the logs, the
    README and the work arrays, that differs from the commit. The footer of a figure names
    that commit, so the figure must be what the commit makes.
    """

    def git(*arguments):
        completed = subprocess.run(
            ["git", "-C", str(HERE), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            sys.exit(f"git {' '.join(arguments)} failed: {completed.stderr.strip()}")
        return completed.stdout.strip()

    dirty = git(
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        ".",
        ":(exclude)logs",
        ":(exclude)README.md",
        ":(exclude)work",
    )
    if dirty:
        sys.exit("refusing to draw from a dirty tree:\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    today = datetime.date.today()
    return commit, f"{today.day} {today:%B %Y}"
