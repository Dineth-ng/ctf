"""Reset the intentionally vulnerable Stage 4 without deleting CTFd data."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    seed = (ROOT / "challenges/stage4-web/database/init.sql").read_bytes()
    subprocess.run(
        ["docker", "compose", "exec", "-T", "stage4-db", "sh", "-c",
         'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u "$MYSQL_USER" "$MYSQL_DATABASE"'],
        input=seed, cwd=ROOT, check=True,
    )
    subprocess.run(
        ["docker", "compose", "up", "-d", "--no-deps", "--force-recreate",
         "--wait", "stage4-web"], cwd=ROOT, check=True,
    )
    print("Stage 4 users and sessions reset. CTFd scores and other stages were kept.")


if __name__ == "__main__":
    main()
