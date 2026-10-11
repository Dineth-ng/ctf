#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * NEXACORE DYNAMICS // PROJECT PROMETHEUS SECURE ENCLAVE
 * VAULT REVERSE-ENGINEERING CHALLENGE
 */

#define VAULT_XOR_KEY 0x5A

void banner(void) {
    puts("=================================================");
    puts("   PROJECT PROMETHEUS SECURE STORAGE ENCLAVE     ");
    puts("   GhostByte Custom Locking Utility v2.4.1       ");
    puts("=================================================");
}

int main(int argc, char *argv[]) {
    banner();

    if (argc != 2) {
        printf("Usage: %s <path_to_encrypted_vault_file>\n", argv[0]);
        printf("Example: %s /opt/vault/vault.enc\n", argv[0]);
        return 1;
    }

    const char *filepath = argv[1];
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        perror("[-] Error opening target vault file");
        return 1;
    }

    fseek(fp, 0, SEEK_END);
    long filesize = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    if (filesize <= 0) {
        fprintf(stderr, "[-] Vault file is empty.\n");
        fclose(fp);
        return 1;
    }

    unsigned char *buffer = (unsigned char *)malloc(filesize);
    if (!buffer) {
        fprintf(stderr, "[-] Memory allocation failed.\n");
        fclose(fp);
        return 1;
    }

    size_t read_bytes = fread(buffer, 1, filesize, fp);
    fclose(fp);

    printf("[+] Successfully loaded %ld encrypted bytes.\n", (long)read_bytes);
    printf("[+] Executing Prometheus neural decrypt loop...\n\n");
    printf("----------------- UNLOCKED VAULT DATA -----------------\n");

    for (size_t i = 0; i < read_bytes; i++) {
        // Core XOR decryption logic (students identify this key in Ghidra / objdump)
        unsigned char decrypted_byte = buffer[i] ^ VAULT_XOR_KEY;
        putchar(decrypted_byte);
    }

    printf("\n-------------------------------------------------------\n");
    printf("[+] Enclave status: PROMETHEUS RESTORED. ATTACK PREVENTED.\n");

    free(buffer);
    return 0;
}
