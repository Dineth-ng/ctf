"""Check generated Stage 5 files against the private organizer manifest."""

from __future__ import annotations

import importlib.util
import io
import json
import struct
import zipfile
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
    disk_bytes = (files / "NH-048-disk.img").read_bytes()
    assert b"NH{" not in disk_bytes, "raw disk leaks a flag"

    # Verify that rebuilding produces stable reset files. The deleted archive
    # is stored in FAT12 cluster 2, the first data cluster in this image.
    bytes_per_sector = struct.unpack_from("<H", disk_bytes, 11)[0]
    reserved = struct.unpack_from("<H", disk_bytes, 14)[0]
    fats = disk_bytes[16]
    root_entries = struct.unpack_from("<H", disk_bytes, 17)[0]
    sectors_per_fat = struct.unpack_from("<H", disk_bytes, 22)[0]
    root = (reserved + fats * sectors_per_fat) * bytes_per_sector
    root_sectors = (root_entries * 32 + bytes_per_sector - 1) // bytes_per_sector
    data_start = root + root_sectors * bytes_per_sector
    deleted_entry = disk_bytes[root + 32:root + 64]
    archive_size = struct.unpack_from("<I", deleted_entry, 28)[0]
    with zipfile.ZipFile(io.BytesIO(disk_bytes[data_start:data_start + archive_size])) as archive:
        assert archive.getinfo("evidence.txt").date_time == (2026, 1, 1, 0, 0, 0)
    print("Stage 5 network and deleted-disk checks passed.")


if __name__ == "__main__":
    main()
