"""Small cross-platform check that the local scoreboard and web stages answer."""

from __future__ import annotations

import sys
import os
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def stage4_port() -> str:
    if "STAGE4_PORT" in os.environ:
        return os.environ["STAGE4_PORT"]
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("STAGE4_PORT="):
                return line.split("=", 1)[1].strip()
    return "8084"


def main() -> int:
    targets = (
        ("CTFd", "http://127.0.0.1:8000/"),
        ("Stage 1", "http://127.0.0.1:8081/"),
        ("Stage 4", f"http://127.0.0.1:{stage4_port()}/legacy/auth/"),
    )
    failures = 0
    for name, url in targets:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                status = response.status
            print(f"{name}: HTTP {status}")
            if status != 200:
                failures += 1
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"{name}: unavailable ({error})")
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
