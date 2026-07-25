"""Единая точка запуска тестов бэкенда.

Запуск из корня проекта:
    python backend/run_tests.py

Дополнительные аргументы передаются напрямую pytest:
    python backend/run_tests.py -k citation -x
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=apps",
        "--cov-report=term-missing",
        *sys.argv[1:],
    ]
    return subprocess.call(command, cwd=BACKEND_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
