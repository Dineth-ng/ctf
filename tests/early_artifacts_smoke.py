"""Check that the first three player artifacts match their intended sources."""

from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "nighthawk-artifact-tools:local"


def docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "run", "--rm", "-v", f"{ROOT}:/work", "-w", "/work", IMAGE, *args],
        text=True, capture_output=True, cwd=ROOT, check=False,
    )


def main() -> None:
    photo = "challenges/stage1-osint/website/assets/images/conference-2026.jpg"
    metadata = docker("exiftool", "-j", photo)
    assert metadata.returncode == 0, metadata.stderr
    comment = json.loads(metadata.stdout)[0]["Comment"]
    assert "NH{metadata_exposure_confirmed}" in comment
    assert "NC-RD-7741" in comment and "PROMETHEUS" in comment

    stego = "challenges/stage2-stego/files/research-archive-stego.jpg"
    extract = f"steghide extract -sf {stego} -p NC-RD-7741 -xf /tmp/note.txt -f >/dev/null && cat /tmp/note.txt"
    recovered = docker("bash", "-lc", extract)
    assert recovered.returncode == 0, recovered.stderr
    assert "NH{covert_channel_discovered}" in recovered.stdout
    assert "GB-COMM-03" in recovered.stdout and "ORPHEUS" in recovered.stdout
    wrong = docker("steghide", "extract", "-sf", stego, "-p", "wrong-password",
                   "-xf", "/tmp/wrong.txt", "-f")
    assert wrong.returncode != 0 and "NH{" not in wrong.stdout

    stage3 = ROOT / "challenges/stage3-crypto"
    ciphertext = base64.b64decode((stage3 / "files/GB-COMM-03.enc").read_text(),
                                  validate=True).decode()
    key = "ORPHEUS"
    plaintext = []
    index = 0
    for char in ciphertext:
        if char.isalpha():
            base = ord("A" if char.isupper() else "a")
            shift = ord(key[index % len(key)]) - ord("A")
            plaintext.append(chr((ord(char) - base - shift) % 26 + base))
            index += 1
        else:
            plaintext.append(char)
    assert "".join(plaintext) == (stage3 / "source/GB-COMM-03-plaintext.txt").read_text()
    print("Stage 1 metadata, Stage 2 extraction/rejection, and Stage 3 decryption passed.")


if __name__ == "__main__":
    main()
