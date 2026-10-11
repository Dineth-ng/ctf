"""Create private lab secrets, Stage 5 artifacts, and Stage 6 build inputs.

The manifest is created once and ignored by Git. Rerunning this script keeps the
same flags and credentials, so CTFd entries remain valid after a reset.
"""

from __future__ import annotations

import json
import secrets
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".organizer"
MANIFEST = PRIVATE / "lab-secrets.json"
VAULT_OUTPUT = ROOT / "challenges" / "stage6-vault" / "generated"


def new_manifest() -> dict[str, str]:
    return {
        "stage5a_flag": f"NH{{network_trace_{secrets.token_hex(5)}}}",
        "stage5b_flag": f"NH{{deleted_note_{secrets.token_hex(5)}}}",
        "stage6_flag": f"NH{{prometheus_vault_{secrets.token_hex(6)}}}",
        "vault_user": "investigator",
        "vault_password": "NV-" + secrets.token_urlsafe(10),
        "vault_code_a": secrets.token_hex(5).upper(),
        "vault_code_b": secrets.token_hex(5).upper(),
    }


def main() -> None:
    PRIVATE.mkdir(exist_ok=True)
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        print("Using the existing private organizer manifest.")
    else:
        manifest = new_manifest()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("Created a new private organizer manifest.")
    VAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    full_code = f"{manifest['vault_code_a']}-{manifest['vault_code_b']}"
    encoded = ", ".join(f"0x{byte ^ 0x5a:02x}" for byte in full_code.encode("ascii"))
    (VAULT_OUTPUT / "vault_config.h").write_text(
        f"#define EXPECTED_LENGTH {len(full_code)}\n"
        f"static const unsigned char encoded_code[EXPECTED_LENGTH] = {{{encoded}}};\n",
        encoding="utf-8",
    )
    (VAULT_OUTPUT / "flag.txt").write_text(manifest["stage6_flag"] + "\n", encoding="utf-8")
    (VAULT_OUTPUT / "password.txt").write_text(manifest["vault_password"] + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "challenges" / "stage5-forensics" / "generate.py")], check=True)
    print("Private flags are in .organizer/lab-secrets.json; do not commit or share it with players.")


if __name__ == "__main__":
    main()
