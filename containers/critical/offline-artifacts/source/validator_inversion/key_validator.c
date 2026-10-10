/*
 * RECOVERED ARTIFACT 2 — Custom Key Validator
 *
 * The player must recover a 16-byte evidence key by reversing the validation
 * loop. The correct key is never stored as plaintext in the compiled binary.
 * This is intentionally simple, deterministic and suitable for ordinary
 * objdump/readelf/strings analysis; it is not a cryptographic password system.
 */
#include <stdio.h>
#include <string.h>

#define KEY_LENGTH 16
#define FLAG_LENGTH 24

static unsigned char rotl8(unsigned char value, unsigned int count) {
    return (unsigned char)((value << count) | (value >> (8U - count)));
}

static int validate_key(const char *candidate) {
    static const unsigned char salt[KEY_LENGTH] = {
        0x31, 0xA7, 0x5C, 0xD2, 0x48, 0x9E, 0x13, 0xE4,
        0x76, 0x2B, 0xC1, 0x54, 0x8D, 0x3F, 0xB0, 0x69
    };
    static const unsigned char expected[KEY_LENGTH] = {
        0xCA, 0xBF, 0x70, 0x79, 0x21, 0xB5, 0xF8, 0xA6,
        0x44, 0xC0, 0x1D, 0x18, 0x7E, 0x67, 0x9C, 0x90
    };
    size_t length = strlen(candidate);

    if (length != KEY_LENGTH) {
        return 0;
    }

    for (size_t index = 0; index < KEY_LENGTH; ++index) {
        unsigned char mixed = (unsigned char)candidate[index] ^ salt[index];
        unsigned char transformed = rotl8(mixed, (unsigned int)((index % 5U) + 1U));
        if (transformed != expected[index]) {
            return 0;
        }
    }
    return 1;
}

static void print_flag(void) {
    static const unsigned char masked_flag[FLAG_LENGTH] = {
        0xE6, 0xF1, 0xE3, 0xDE, 0xC0, 0xC2, 0xC2, 0x97,
        0xFA, 0xD3, 0xC4, 0xC9, 0xCC, 0xC1, 0xC4, 0xD1,
        0xCA, 0xD7, 0xFA, 0xD5, 0xC4, 0xD1, 0xCD, 0xD8
    };

    fputs("Evidence seal: ", stdout);
    for (size_t index = 0; index < FLAG_LENGTH; ++index) {
        putchar((int)(masked_flag[index] ^ 0xA5U));
    }
    putchar('\n');
}

int main(void) {
    char candidate[64];

    puts("=== LOCAL_CONTROL_SERVICE'S RECOVERED ARTIFACT 2: Evidence Key Validator ===");
    puts("A protected archive accepts a fixed-length recovery key.");
    fputs("Recovery key> ", stdout);

    if (fgets(candidate, sizeof(candidate), stdin) == NULL) {
        fputs("No key supplied.\n", stderr);
        return 2;
    }
    candidate[strcspn(candidate, "\r\n")] = '\0';

    if (!validate_key(candidate)) {
        puts("Archive remains sealed.");
        return 1;
    }

    puts("Archive seal accepted. THREAD_02 recovery access recorded.");
    print_flag();
    return 0;
}
