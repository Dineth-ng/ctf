"""Organizer check: recover Stage 5 evidence from the generated files."""

from __future__ import annotations

import base64
import io
import struct
import zipfile
from pathlib import Path


FILES = Path(__file__).resolve().parent / "files"


def recover_network(path: Path) -> str:
    data = path.read_bytes()
    if data[:4] != b"\xd4\xc3\xb2\xa1":
        raise ValueError("Expected a little-endian Ethernet PCAP")
    cursor = 24
    parts: dict[int, bytes] = {}
    while cursor + 16 <= len(data):
        _, _, length, _ = struct.unpack_from("<IIII", data, cursor)
        cursor += 16
        frame = data[cursor:cursor + length]
        cursor += length
        if len(frame) < 54 or frame[12:14] != b"\x08\x00":
            continue
        ip_size = (frame[14] & 15) * 4
        tcp_at = 14 + ip_size
        tcp_size = (frame[tcp_at + 12] >> 4) * 4
        payload = frame[tcp_at + tcp_size:]
        if not payload.startswith(b"POST /api/ingest?case=NH-048"):
            continue
        headers, body = payload.split(b"\r\n\r\n", 1)
        for line in headers.split(b"\r\n"):
            if line.lower().startswith(b"x-archive-part: "):
                number = int(line.split(b": ", 1)[1].split(b"/", 1)[0])
                parts[number] = body
    if sorted(parts) != [1, 2]:
        raise ValueError("Both ordered archive parts were not recovered")
    return base64.b64decode(parts[1] + parts[2], validate=True).decode()


def recover_deleted_file(path: Path) -> str:
    image = path.read_bytes()
    if image[510:512] != b"\x55\xaa":
        raise ValueError("Invalid FAT boot signature")
    bytes_per_sector = struct.unpack_from("<H", image, 11)[0]
    sectors_per_cluster = image[13]
    reserved = struct.unpack_from("<H", image, 14)[0]
    fats = image[16]
    root_entries = struct.unpack_from("<H", image, 17)[0]
    sectors_per_fat = struct.unpack_from("<H", image, 22)[0]
    root = (reserved + fats * sectors_per_fat) * bytes_per_sector
    data_start = root + ((root_entries * 32 + bytes_per_sector - 1) // bytes_per_sector) * bytes_per_sector
    for position in range(root, root + root_entries * 32, 32):
        entry = image[position:position + 32]
        if entry[0] != 0xE5 or entry[1:11] != b"VIDENCEZIP":
            continue
        cluster = struct.unpack_from("<H", entry, 26)[0]
        length = struct.unpack_from("<I", entry, 28)[0]
        if cluster < 2 or length > bytes_per_sector * sectors_per_cluster:
            raise ValueError("Deleted archive has invalid cluster or length")
        offset = data_start + (cluster - 2) * sectors_per_cluster * bytes_per_sector
        with zipfile.ZipFile(io.BytesIO(image[offset:offset + length])) as archive:
            return archive.read("evidence.txt").decode()
    raise ValueError("Deleted EVIDENCE.ZIP entry not found")


def main() -> None:
    print(recover_network(FILES / "NH-048-traffic.pcap"))
    print(recover_deleted_file(FILES / "NH-048-disk.img"))


if __name__ == "__main__":
    main()
