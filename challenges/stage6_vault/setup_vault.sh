#!/bin/bash
set -e

# Compile the vault_lock binary
gcc -O2 -fno-stack-protector -o /opt/vault/vault_lock /tmp/vault_lock.c

# Encrypt the final flag into vault.enc using XOR key 0x5A
python3 -c '
flag = (
    "===========================================================\n"
    "NEXACORE DYNAMICS: PROMETHEUS CORE RECOVERY CONFIRMED\n"
    "===========================================================\n"
    "All autonomous cyber-defense weights and patents preserved.\n\n"
    "FINAL OPERATION NIGHTHAWK FLAG:\n"
    "NH{pr0m3th3us_c0r3_s4f3gu4rd3d}\n\n"
    "Incident Status: THREAT NEUTRALIZED. INSIDER EXPOSED.\n"
    "===========================================================\n"
).encode("utf-8")

key = 0x5A
encrypted = bytes([b ^ key for b in flag])
with open("/opt/vault/vault.enc", "wb") as f:
    f.write(encrypted)
'

# Create low-privilege user
useradd -m -s /bin/bash runner || true
echo "runner:nighthawk_guest" | chpasswd

# Setup directory permissions:
# Low privilege user 'runner' cannot read /opt/vault directly!
chown -R root:root /opt/vault
chmod 700 /opt/vault
chmod 600 /opt/vault/vault.enc
chmod 755 /opt/vault/vault_lock

# Privilege Escalation vector via SUID or Sudoers:
# Runner can execute /usr/bin/find as root with NO PASSWORD (GTFOBins classic)
echo "runner ALL=(ALL) NOPASSWD: /usr/bin/find" > /etc/sudoers.d/runner
chmod 440 /etc/sudoers.d/runner

# Add a welcome message in runner home
cat << 'MSG' > /home/runner/README.txt
=============================================================
WELCOME TO NEXACORE STORAGE NODE - RECOVERY SHELL
=============================================================
You have accessed the storage node via the credentials recovered
from Stage 5 disk forensics (user: runner).

MISSION:
1. Enumerate your permissions to elevate to root.
2. Locate GhostByte's locked repository in /opt/vault/.
3. Reverse-engineer the vault decryption binary (vault_lock)
   and unlock /opt/vault/vault.enc to extract the final flag.
=============================================================
MSG
chown runner:runner /home/runner/README.txt

rm -f /tmp/vault_lock.c
echo "[+] Vault environment initialized."
