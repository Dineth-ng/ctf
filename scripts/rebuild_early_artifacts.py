"""Align the checked-in Stage 1–3 player artifacts with their source files.

ExifTool and steghide run inside a small Docker image, so the host does not
need Linux packages installed. This intentionally changes tracked JPEG files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "nighthawk-artifact-tools:local"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def docker(*args: str) -> None:
    run("docker", "run", "--rm", "-v", f"{ROOT}:/work", "-w", "/work", IMAGE, *args)


def main() -> None:
    found = subprocess.run(["docker", "image", "inspect", IMAGE], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=False)
    if found.returncode != 0:
        run("docker", "build", "--network", "host", "-t", IMAGE, "tools")
    docker("bash", "challenges/stage1-osint/generator/generate_stage1.sh")
    docker("steghide", "embed", "-cf",
           "challenges/stage2-stego/files/research-archive.jpg", "-ef",
           "challenges/stage2-stego/source/ghostbyte-note.txt", "-sf",
           "challenges/stage2-stego/files/research-archive-stego.jpg", "-p",
           "NC-RD-7741", "-f")
    run(sys.executable, "challenges/stage3-crypto/generator/generate_stage3.py")
    print("Stages 1–3 artifacts rebuilt. Review the JPEG and encrypted file diff.")


if __name__ == "__main__":
    main()
