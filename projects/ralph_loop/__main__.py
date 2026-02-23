import sys
from pathlib import Path

# When invoked as `python -m ralph_loop`, Python adds the parent of the package
# (projects/) to sys.path but not ralph_loop/ itself. Insert it so that `libs`
# and `main` are importable without any package prefix.
sys.path.insert(0, str(Path(__file__).parent))

from main import main  # noqa: E402

main()
