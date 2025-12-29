import sys
from pathlib import Path


# Ensure the `src/` directory is on sys.path so tests can import the installed
# package style (`extremistan`) as well as the `src.extremistan` namespace used
# in some modules.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))
