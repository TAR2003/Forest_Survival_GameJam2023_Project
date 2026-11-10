#!/usr/bin/env python3
"""Check the forest package and, without --check, copy it into dist/."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE = ["main.py", "src", "pictures", "audio", "data", "assets"]


def missing_paths():
    return [name for name in PACKAGE if not (ROOT / name).exists()]


def run_pytest():
    env = os.environ.copy()
    env.setdefault("SDL_VIDEODRIVER", "dummy")
    env.setdefault("SDL_AUDIODRIVER", "dummy")
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        env=env,
    ).returncode


def copy_package():
    dest = ROOT / "dist" / "forest_survival"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in PACKAGE:
        source = ROOT / name
        target = dest / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    print(f"Copied the game to {dest}")


def main():
    missing = missing_paths()
    if missing:
        print("Missing: " + ", ".join(missing))
        return 1
    code = run_pytest()
    if code != 0:
        return code
    if "--check" in sys.argv:
        print("Deploy check passed")
        return 0
    copy_package()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
