/* Intentionally small SUID teaching program. Run only inside the isolated lab. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vault_config.h"

int main(void) {
    char entered[128];
    char audit_entered[128];
    char audit_expected[32];
    unsigned char expected[EXPECTED_LENGTH + 1];
    FILE *vault;
    char flag[256];
    size_t index;

    for (index = 0; index < EXPECTED_LENGTH; ++index) {
        expected[index] = encoded_code[index] ^ 0x5a;
    }
    expected[EXPECTED_LENGTH] = '\0';
    puts("Prometheus Vault recovery console");
    fputs("Recovery code: ", stdout);
    fflush(stdout);
    if (fgets(entered, sizeof(entered), stdin) == NULL) {
        return 1;
    }
    entered[strcspn(entered, "\r\n")] = '\0';
    if (strlen(entered) != EXPECTED_LENGTH || strcmp(entered, (char *)expected) != 0) {
        puts("Recovery code rejected.");
        return 2;
    }
    /* The second check makes inspecting the executable part of the task. */
    unsigned long long first = strtoull(entered, NULL, 16);
    unsigned long long second = strtoull(entered + 11, NULL, 16);
    unsigned long long challenge = (first ^ second ^ 0x5A3C19F0D2ULL) & 0xFFFFFFFFFFULL;
    snprintf(audit_expected, sizeof(audit_expected), "%010llX", challenge);
    fputs("Audit response: ", stdout);
    fflush(stdout);
    if (fgets(audit_entered, sizeof(audit_entered), stdin) == NULL) {
        return 1;
    }
    audit_entered[strcspn(audit_entered, "\r\n")] = '\0';
    if (strcmp(audit_entered, audit_expected) != 0) {
        puts("Audit response rejected.");
        return 2;
    }
    vault = fopen("/root/prometheus/flag.txt", "r");
    if (vault == NULL || fgets(flag, sizeof(flag), vault) == NULL) {
        fputs("Vault storage unavailable.\n", stderr);
        return 3;
    }
    fclose(vault);
    printf("Vault evidence: %s", flag);
    return 0;
}
