#!/usr/bin/env python3
import base64

key = "PROMETHEUS"
with open("chat_log.txt", "r") as f:
    lines = f.readlines()

payload = ""
for line in lines:
    line = line.strip()
    if line and not line.startswith("===") and not line.startswith("Source:") and not line.startswith("Protocol:") and not line.startswith("Hint:") and not line.startswith("CIPHERTEXT"):
        payload = line
        break

b64_dec = base64.b64decode(payload).decode('utf-8')

plaintext = []
k_idx = 0
for char in b64_dec:
    if char.isalpha():
        base = ord('A') if char.isupper() else ord('a')
        shift = ord(key[k_idx % len(key)].upper()) - ord('A')
        plaintext.append(chr((ord(char) - base - shift) % 26 + base))
        k_idx += 1
    else:
        plaintext.append(char)

print("".join(plaintext))
