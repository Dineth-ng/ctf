"""Verify the optional container's intended and rejected vault paths."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def vault(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "--profile", "vault-container", "exec", "-T",
         "-u", "investigator", "stage6-vault", *args],
        input=input_text, text=True, capture_output=True, cwd=ROOT, check=False,
    )


def main() -> None:
    manifest = json.loads((ROOT / ".organizer/lab-secrets.json").read_text(encoding="utf-8"))
    direct = vault("cat", "/root/prometheus/flag.txt")
    assert direct.returncode != 0, "low-privilege user can read protected flag"
    incorrect = vault("/usr/local/bin/prometheus-vault", input_text="WRONG\n")
    assert incorrect.returncode != 0 and "rejected" in incorrect.stdout
    fragments = f"{manifest['vault_code_a']}-{manifest['vault_code_b']}"
    wrong_audit = vault("/usr/local/bin/prometheus-vault", input_text=fragments + "\nWRONG\n")
    assert wrong_audit.returncode != 0 and "Audit response rejected" in wrong_audit.stdout
    audit = (int(manifest["vault_code_a"], 16)
             ^ int(manifest["vault_code_b"], 16) ^ 0x5A3C19F0D2) & 0xFFFFFFFFFF
    correct = vault("/usr/local/bin/prometheus-vault",
                    input_text=f"{fragments}\n{audit:010X}\n")
    assert correct.returncode == 0 and manifest["stage6_flag"] in correct.stdout, correct
    print("Stage 6 permissions, wrong-code, wrong-audit, and correct-path checks passed.")


if __name__ == "__main__":
    main()
