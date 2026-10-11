#!/usr/bin/env python3
import re

print("[*] Analyzing exfil.pcap for subflag 1...")
with open("exfil.pcap", "rb") as f:
    pcap_data = f.read()

m1 = re.search(b"NH\{[a-zA-Z0-9_]+", pcap_data)
subflag1 = m1.group(0).decode() if m1 else "Not found"
print(f"[+] Found in PCAP: {subflag1}")

print("[*] Carving disk.img unallocated space for subflag 2...")
with open("disk.img", "rb") as f:
    disk_data = f.read()

m2 = re.search(b"SUBFLAG_2:\s*([a-zA-Z0-9_\}]+)", disk_data)
subflag2 = m2.group(1).decode() if m2 else "Not found"
print(f"[+] Found in Disk Image: {subflag2}")

full_flag = subflag1 + subflag2
print(f"[+] COMBINED STAGE 5 FLAG: {full_flag}")
