import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "ui/app.py"),
    ]
    raise SystemExit(subprocess.call(command, cwd=PROJECT_ROOT))


if __name__ == "__main__":
    main()
