# Operation NightHawk: The GhostByte Files

A complete 6-stage Capture The Flag (CTF) cyber defense scenario designed for Year 2–3 cybersecurity students.

## Quick Start (Deploy on Kali Linux)
```bash
cd operation_nighthawk
sudo ./scripts/deploy.sh
```

## Active Services & Ports
| Component | Address / Connection | Notes |
|---|---|---|
| **CTFd Platform** | `http://localhost:8000` | Automated Scoreboard |
| **Stage 1 & 2** | `http://localhost:80` | NexaCore Defaced Portal (OSINT + Stego) |
| **Stage 3** | File: `stage3_crypto/chat_log.txt` | C2 Intercepted Chat (Vigenère + B64) |
| **Stage 4** | `http://localhost:8080` | NexaCore Shadow Relay (SQLi / Auth Bypass) |
| **Stage 5** | Files: `stage5_forensics/` | Wireshark PCAP + Forensic Disk Image |
| **Stage 6** | `ssh -p 2222 runner@localhost` | Password: `nighthawk_guest` |

---

## Stage Guide & Flags Reference

### Stage 1: "The Digital Footprint" (OSINT)
- **Objective:** Find employee info & metadata in `employee.jpg`.
- **Command:** `exiftool employee.jpg`
- **Flag:** `NH{exif_m3t4d4t4_tr4ck3d}`

### Stage 2: "The Hidden Message" (Steganography)
- **Objective:** Extract the hidden text from `trophy.png`.
- **Command:** `python3 extract_lsb.py trophy.png` or `zsteg -a trophy.png`
- **Flag:** `NH{st3g0_gh0st_unh1dd3n}`

### Stage 3: "Encrypted Correspondence" (Cryptography)
- **Objective:** Decode Base64 then decrypt Vigenère with key `PROMETHEUS`.
- **Command:** `python3 solve_stage3.py`
- **Flag:** `NH{v1g3n3r3_c1ph3r_cr4ck3d}`

### Stage 4: "The Backdoor Portal" (Web Security)
- **Objective:** Log into `http://localhost:8080` using credentials `admin` / `GhostOpsPass2026!` or via SQL injection `' OR 1=1#`.
- **Flag:** `NH{sqli_4dm1n_p0rt4l_byp4ss}`

### Stage 5: "Tracing the Exfiltration" (Forensics & Network)
- **Objective:** Carve FTP packet in `exfil.pcap` + carve deleted block in `disk.img`.
- **Command:** `python3 solve_stage5.py`
- **Flag:** `NH{pcap_ftp_tr4ff1c_4nd_d1sk_r3c0v3ry}`

### Stage 6: "The Prometheus Vault" (Reverse Engineering & PrivEsc)
- **Objective:**
  1. SSH: `ssh -p 2222 runner@localhost` (Password: `nighthawk_guest`)
  2. PrivEsc via sudo: `sudo find . -exec /bin/sh \; -quit`
  3. Reverse & Decrypt: `/opt/vault/vault_lock /opt/vault/vault.enc`
- **Flag:** `NH{pr0m3th3us_c0r3_s4f3gu4rd3d}`
