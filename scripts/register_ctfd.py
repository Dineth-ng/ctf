"""Register the seven scoring challenges in an already configured local CTFd.

An organizer API token is required in CTFD_TOKEN. Existing challenges are reused;
the script refuses to silently replace an existing, different flag.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("CTFD_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.environ.get("CTFD_TOKEN", "")
if not TOKEN:
    credential_file = ROOT / ".organizer" / "ctfd-admin.json"
    if credential_file.exists():
        TOKEN = json.loads(credential_file.read_text(encoding="utf-8")).get("token", "")


def local_env_value(key: str, default: str) -> str:
    if key in os.environ:
        return os.environ[key]
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"\'')
    return default


def request(method: str, path: str, payload: dict | None = None,
            *, raw: bytes | None = None, content_type: str = "application/json") -> object:
    url = BASE + "/api/v1/" + path.lstrip("/")
    data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Token " + TOKEN,
                                          "Content-Type": content_type,
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"CTFd {method} {path}: HTTP {exc.code}: {detail}") from exc
    if not result.get("success"):
        raise RuntimeError(f"CTFd {method} {path}: {result.get('errors', result)}")
    return result.get("data")


def multipart_upload(challenge_id: int, path: Path) -> None:
    boundary = "----nighthawk" + secrets.token_hex(12)
    parts = []
    for key, value in (("type", "challenge"), ("challenge_id", str(challenge_id))):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
                  f"filename=\"{path.name}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode())
    parts.append(path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    request("POST", "files", raw=b"".join(parts),
            content_type=f"multipart/form-data; boundary={boundary}")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Run scripts/setup_ctfd.py or set CTFD_TOKEN to an organizer API token.")
    if urllib.parse.urlparse(BASE).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("CTFD_URL must be a local loopback address for this lab.")
    manifest_path = ROOT / ".organizer" / "lab-secrets.json"
    if not manifest_path.exists():
        raise SystemExit("Run python scripts/build_lab.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stage4_flag = local_env_value("STAGE4_FLAG", "NH{legacy_portal_bypassed}")
    stage4_port = local_env_value("STAGE4_PORT", "8084")
    challenges = [
        ("Stage 1 - Digital Footprint", "OSINT", 100,
         "A NexaCore conference photo may say more than the public news page. "
         "Explore http://127.0.0.1:8081/ and inspect the original image.",
         "NH{metadata_exposure_confirmed}", None),
        ("Stage 2 - Hidden Message", "Steganography", 200,
         "Use the archive reference from Stage 1 to inspect the attached research photo. "
         "Find the hidden GhostByte field note.",
         "NH{covert_channel_discovered}",
         ROOT / "challenges/stage2-stego/files/research-archive-stego.jpg"),
        ("Stage 3 - Encrypted Correspondence", "Cryptography", 250,
         "The field note names a channel and a crypto reference. Decode the attached "
         "correspondence to find the legacy gateway.",
         "NH{communications_decrypted}",
         ROOT / "challenges/stage3-crypto/files/GB-COMM-03.enc"),
        ("Stage 4 - Backdoor Portal", "Web Security", 300,
         "Investigate the legacy authentication flow and locate incident NH-048. "
         f"Local gateway: http://127.0.0.1:{stage4_port}/legacy/auth/",
         stage4_flag, None),
        ("Stage 5A - Exfiltration Trace", "Network Forensics", 350,
         "Incident NH-048 includes a packet capture. Follow the HTTP traffic and "
         "reconstruct the split archive message.",
         manifest["stage5a_flag"],
         ROOT / "challenges/stage5-forensics/files/NH-048-traffic.pcap"),
        ("Stage 5B - Deleted Evidence", "Disk Forensics", 400,
         "A FAT12 disk image contains a deleted evidence archive. Recover it and "
         "retain its vault handoff details.",
         manifest["stage5b_flag"],
         ROOT / "challenges/stage5-forensics/files/NH-048-disk.img"),
        ("Stage 6 - Prometheus Vault", "Linux / Reverse Engineering", 500,
         "Use the login and two-part recovery code from the forensic evidence on "
         "the dedicated vault VM. Inspect /usr/local/bin/prometheus-vault. "
         "Ask the organizer for the host-only VM address; never use a public host.",
         manifest["stage6_flag"], None),
    ]
    hints = {
        "Stage 1 - Digital Footprint": "The original image file can hold metadata that a screenshot loses.",
        "Stage 2 - Hidden Message": "Try a steganography extraction tool with the archive reference.",
        "Stage 3 - Encrypted Correspondence": "Decode the outer layer first; then try the note's crypto reference as a key.",
        "Stage 4 - Backdoor Portal": "Inspect the login request and how a single quote is handled.",
        "Stage 5A - Exfiltration Trace": "Filter the HTTP requests by the archive host and inspect X-Archive-Part.",
        "Stage 5B - Deleted Evidence": "Look at deleted FAT12 root-directory entries, then recover the file they point to.",
        "Stage 6 - Prometheus Vault": "Check file permissions and inspect how the binary calculates the audit response.",
    }
    # CTFd's ordinary list hides unsolved prerequisites even from an admin.
    # The explicit admin view includes every locked challenge for safe reruns.
    listed = request("GET", "challenges?view=admin")
    existing = {item["name"]: item for item in listed}
    if len(existing) != len(listed):
        raise RuntimeError("Duplicate challenge names exist in CTFd; resolve them before rerunning.")
    previous_id: int | None = None
    for name, category, value, description, flag, artifact in challenges:
        challenge = existing.get(name)
        if challenge is None:
            challenge = request("POST", "challenges", {
                "name": name, "category": category, "description": description,
                "type": "standard", "value": value, "state": "visible"})
            print(f"Created {name}")
        else:
            print(f"Reusing {name}")
        challenge_id = challenge["id"]
        requirements = request("GET", f"challenges/{challenge_id}/requirements") or {}
        if previous_id is not None:
            prerequisites = requirements.get("prerequisites", [])
            if prerequisites and prerequisites != [previous_id]:
                raise RuntimeError(f"{name} has different prerequisites; review them in CTFd.")
            if not prerequisites:
                request("PATCH", f"challenges/{challenge_id}",
                        {"requirements": {"prerequisites": [previous_id]}})
                print("  Linked to the previous challenge")
        flags = request("GET", f"challenges/{challenge_id}/flags")
        if flags and not any(item["content"] == flag for item in flags):
            raise RuntimeError(f"{name} already has a different flag; review it in CTFd.")
        if not flags:
            request("POST", "flags", {"challenge_id": challenge_id, "type": "static",
                                      "content": flag, "data": "case_sensitive"})
            print("  Added its static flag")
        registered_hints = request("GET", f"challenges/{challenge_id}/hints")
        if not any(item["content"] == hints[name] for item in registered_hints):
            request("POST", "hints", {"challenge_id": challenge_id, "type": "standard",
                                      "content": hints[name], "cost": 0})
            print("  Added a free hint")
        if artifact is not None:
            if not artifact.is_file():
                raise FileNotFoundError(artifact)
            files = request("GET", f"challenges/{challenge_id}/files")
            if not any(Path(item["location"]).name == artifact.name for item in files):
                multipart_upload(challenge_id, artifact)
                print(f"  Uploaded {artifact.name}")
        previous_id = challenge_id
    print("Registration finished. Check the player view and test correct and incorrect submissions.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, FileNotFoundError, urllib.error.URLError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
