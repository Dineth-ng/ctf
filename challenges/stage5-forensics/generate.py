"""Build fictional Stage 5 network and deleted-file evidence using the standard library.

Run from the repository root after scripts/build_lab.py has created the local
organizer manifest. None of the traffic or identities comes from a real system.
"""

from __future__ import annotations

import base64
import io
import json
import struct
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / ".organizer" / "lab-secrets.json"
OUTPUT = Path(__file__).resolve().parent / "files"


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def address(text: str) -> bytes:
    return bytes(int(piece) for piece in text.split("."))


def packet(source: str, destination: str, source_port: int, destination_port: int,
           sequence: int, acknowledgement: int, flags: int, payload: bytes, ident: int) -> bytes:
    src, dst = address(source), address(destination)
    tcp_without_sum = struct.pack("!HHIIHHHH", source_port, destination_port,
                                  sequence, acknowledgement, (5 << 12) | flags,
                                  65535, 0, 0)
    pseudo = src + dst + struct.pack("!BBH", 0, 6, len(tcp_without_sum) + len(payload))
    tcp_sum = checksum(pseudo + tcp_without_sum + payload)
    tcp = struct.pack("!HHIIHHHH", source_port, destination_port, sequence,
                      acknowledgement, (5 << 12) | flags, 65535, tcp_sum, 0)
    ip_without_sum = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp) + len(payload),
                                 ident, 0x4000, 64, 6, 0, src, dst)
    ip_sum = checksum(ip_without_sum)
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp) + len(payload),
                     ident, 0x4000, 64, 6, ip_sum, src, dst)
    ethernet = bytes.fromhex("0200000000020200000000010800")
    return ethernet + ip + tcp + payload


def http_post(host: str, route: str, body: bytes, archive_part: str | None = None) -> bytes:
    headers = [f"POST {route} HTTP/1.1", f"Host: {host}",
               "Content-Type: application/octet-stream", f"Content-Length: {len(body)}",
               "Connection: close"]
    if archive_part:
        headers.append(f"X-Archive-Part: {archive_part}")
    return ("\r\n".join(headers) + "\r\n\r\n").encode() + body


def make_pcap(secrets: dict[str, str]) -> bytes:
    message = (
        "NH-048 / GhostByte exfiltration trace\n"
        f"Stage 5A flag: {secrets['stage5a_flag']}\n"
        f"Vault code, first half: {secrets['vault_code_a']}\n"
        "The second half and vault login are in the recovered disk note.\n"
    ).encode()
    encoded = base64.b64encode(message)
    midpoint = len(encoded) // 2
    chunks = [encoded[:midpoint], encoded[midpoint:]]
    requests = [
        http_post("telemetry.nexacore.local", "/health", b"status=ok"),
        http_post("archive.nexacore.local", "/api/ingest?case=NH-048", chunks[1], "2/2"),
        http_post("telemetry.nexacore.local", "/metrics", b"count=7"),
        http_post("archive.nexacore.local", "/api/ingest?case=NH-048", chunks[0], "1/2"),
    ]
    result = bytearray(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    timestamp = 1_790_000_000
    ident = 100
    for index, request in enumerate(requests):
        source_port = 41000 + index
        client_seq, server_seq = 1000 + 10000 * index, 5000 + 10000 * index
        frames = [
            packet("10.77.5.24", "10.77.5.80", source_port, 80, client_seq, 0, 0x02, b"", ident),
            packet("10.77.5.80", "10.77.5.24", 80, source_port, server_seq, client_seq + 1, 0x12, b"", ident + 1),
            packet("10.77.5.24", "10.77.5.80", source_port, 80, client_seq + 1, server_seq + 1, 0x10, b"", ident + 2),
            packet("10.77.5.24", "10.77.5.80", source_port, 80, client_seq + 1, server_seq + 1, 0x18, request, ident + 3),
        ]
        for frame in frames:
            result.extend(struct.pack("<IIII", timestamp, ident, len(frame), len(frame)))
            result.extend(frame)
            ident += 1
        timestamp += 3
    return bytes(result)


def make_fat12(secrets: dict[str, str]) -> bytes:
    """A small valid FAT12 floppy image with a deleted text directory entry."""
    disk = bytearray(1_474_560)
    boot = disk[:512]
    boot[0:3] = b"\xeb\x3c\x90"
    boot[3:11] = b"MSDOS5.0"
    struct.pack_into("<HBHBHHBHHHII", boot, 11, 512, 1, 1, 2, 224, 2880,
                     0xF0, 9, 18, 2, 0, 0)
    boot[510:512] = b"\x55\xaa"
    disk[:512] = boot
    for offset in (512, 512 + 9 * 512):
        disk[offset:offset + 3] = b"\xf0\xff\xff"
        # Cluster 2 is deliberately marked free after deletion.
        disk[offset + 4] = 0xF0
        disk[offset + 5] = 0xFF
    root_offset = (1 + 2 * 9) * 512
    data_offset = (1 + 2 * 9 + 14) * 512
    readme = b"NH-048 evidence image. A deleted operations archive was recovered from this volume.\r\n"
    note = (
        "NH-048 deleted operations note\r\n"
        f"Stage 5B flag: {secrets['stage5b_flag']}\r\n"
        f"Vault login: {secrets['vault_user']}\r\n"
        f"Vault password: {secrets['vault_password']}\r\n"
        f"Vault code, second half: {secrets['vault_code_b']}\r\n"
        "Present the two vault fragments with a hyphen; inspect the vault binary for its audit response.\r\n"
    ).encode()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_output:
        # A normal ZipInfo uses the current clock time. That made the disk image
        # change on every rebuild even though the challenge answers stayed the
        # same. Keep the metadata fixed so reset/recovery is reproducible.
        evidence_info = zipfile.ZipInfo("evidence.txt", date_time=(2026, 1, 1, 0, 0, 0))
        evidence_info.compress_type = zipfile.ZIP_DEFLATED
        evidence_info.external_attr = 0o644 << 16
        zip_output.writestr(evidence_info, note)
    deleted_file = archive.getvalue()
    if len(deleted_file) > 512:
        raise ValueError("The deleted archive must fit in one disk cluster")
    def entry(offset: int, name: bytes, cluster: int, size: int) -> None:
        disk[offset:offset + 11] = name
        disk[offset + 11] = 0x20
        struct.pack_into("<H", disk, offset + 26, cluster)
        struct.pack_into("<I", disk, offset + 28, size)
    entry(root_offset, b"README  TXT", 3, len(readme))
    entry(root_offset + 32, b"\xe5VIDENCEZIP", 2, len(deleted_file))
    disk[data_offset:data_offset + len(deleted_file)] = deleted_file
    disk[data_offset + 512:data_offset + 512 + len(readme)] = readme
    return bytes(disk)


def main() -> None:
    secrets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "NH-048-traffic.pcap").write_bytes(make_pcap(secrets))
    (OUTPUT / "NH-048-disk.img").write_bytes(make_fat12(secrets))
    print("Created the fictional NH-048 packet capture and FAT12 disk image.")


if __name__ == "__main__":
    main()
