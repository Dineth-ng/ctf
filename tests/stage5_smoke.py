"""Check generated Stage 5 files against the private organizer manifest."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "challenges/stage5-forensics/solve.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("stage5_solver", MODULE)
    assert spec is not None and spec.loader is not None
    solver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver)
    manifest = json.loads((ROOT / ".organizer/lab-secrets.json").read_text(encoding="utf-8"))
    files = ROOT / "challenges/stage5-forensics/files"
    network = solver.recover_network(files / "NH-048-traffic.pcap")
    disk = solver.recover_deleted_file(files / "NH-048-disk.img")
    assert manifest["stage5a_flag"] in network
    assert manifest["vault_code_a"] in network
    assert manifest["stage5b_flag"] in disk
    assert manifest["vault_code_b"] in disk
    assert manifest["vault_password"] in disk
    assert b"NH{" not in (files / "NH-048-disk.img").read_bytes(), "raw disk leaks a flag"
    print("Stage 5 network and deleted-disk checks passed.")


if __name__ == "__main__":
    main()
