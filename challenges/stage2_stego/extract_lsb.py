#!/usr/bin/env python3
from PIL import Image
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "trophy.png"
img = Image.open(filename)
bits = []
for r, g, b in img.getdata():
    bits.extend([r & 1, g & 1, b & 1])

# Reassemble bytes
raw_bytes = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte = 0
    for j in range(8):
        byte = (byte << 1) | bits[i + j]
    raw_bytes.append(byte)

length = int.from_bytes(raw_bytes[:4], byteorder='big')
if length < len(raw_bytes):
    print("--- Extracted Message ---")
    print(raw_bytes[4:4+length].decode(errors='replace'))
else:
    print("Failed to decode LSB length.")
