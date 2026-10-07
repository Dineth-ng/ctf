import base64
from pathlib import Path

KEY = "ORPHEUS"

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "source" / "GB-COMM-03-plaintext.txt"
OUTPUT_FILE = BASE_DIR / "files" / "GB-COMM-03.enc"


def vigenere_encrypt(text, key):
    result = []
    key_index = 0

    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)].upper()) - ord("A")

            if char.isupper():
                encrypted = chr(
                    (ord(char) - ord("A") + shift) % 26 + ord("A")
                )
            else:
                encrypted = chr(
                    (ord(char) - ord("a") + shift) % 26 + ord("a")
                )

            result.append(encrypted)
            key_index += 1
        else:
            result.append(char)

    return "".join(result)


def main():
    if not INPUT_FILE.exists():
        print(f"[-] Input file not found: {INPUT_FILE}")
        return

    plaintext = INPUT_FILE.read_text()

    encrypted = vigenere_encrypt(plaintext, KEY)

    encoded = base64.b64encode(
        encrypted.encode()
    ).decode()

    OUTPUT_FILE.write_text(encoded)

    print("[+] Stage 3 generated successfully")
    print(f"[+] Output: {OUTPUT_FILE}")
    print("[+] Encryption: Vigenere")
    print("[+] Outer encoding: Base64")


if __name__ == "__main__":
    main()
