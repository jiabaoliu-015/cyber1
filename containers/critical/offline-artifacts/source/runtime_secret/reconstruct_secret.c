/*
 * RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret
 *
 * Reverse Engineering Challenge (Slice D)
 *
 * DESCRIPTION:
 * The important secret/key/credential is reconstructed at runtime via a
 * series of simple mathematical and bitwise operations — NOT stored as
 * obvious plaintext in the binary.
 *
 * RECONSTRUCTION ALGORITHM:
 *   secret_value = ((param1 * 7) + (param2 XOR 0xFF)) * 3
 *                + reverse_byte(param3)
 *                + param4
 *                - ((param5 % 3) * 2)
 *
 * Output: A 4-character hexadecimal digest representing the reconstructed secret
 *
 * KEY INSIGHT: The secret is computed at runtime from embedded constants
 * discovered through disassembly — NOT found by strings alone.
 *
 * INTENDED TOOLS (ordinary reversing tools available to students):
 *   strings, objdump, readelf, nm, equivalent
 *
 * LEARNING OBJECTIVE:
 *  Understanding runtime computation patterns in compiled binaries.
 *
 * PLAYER DISCOVERY PATH:
 *   1. Run the binary and observe how it transforms inputs
 *   2. Use `strings` to scan — but they won't be plaintext
 *   3. Disassemble with objdump/readelf to reverse-engineer the computation
 *   4. Reconstruct the algorithm and determine the inputs yielding the valid credential
 *
 * RESET BEHAVIOR:
 *   The binary outputs the reconstructed secret — no side effects required.
 *
 * DESIGN NOTES:
 *   - Simple transformation — explainable during a student demo
 *   - Deterministic output on every run
 *   - No extreme obfuscation, packers, anti-debugging, undefined behaviour
 *   - No brute-force requirements
 *   - Expected value: derived from algorithm applied to embedded constants
 *
 * -- Slice D Implementation --
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Reverse a byte (bit reversal) — simple operation for educational clarity.
 */
static int reverse_byte(int byte_value)
{
    int result = 0;
    int bit;
    for (int i = 0; i < 8; i++) {
        bit = (byte_value >> i) & 1;
        result |= bit << (7 - i);
    }
    return result;
}

/*
 * Reconstruct the secret using the runtime algorithm.
 * Parameters are derived from the binary's internal constants —
 * discovered through disassembly, not hardcoded in plaintext.
 */
static int reconstruct_secret(int param1, int param2, int param3, int param4, int param5)
{
    /* Step 1: Multiply param1 by 7 */
    int step1 = param1 * 7;

    /* Step 2: XOR param2 with 0xFF (bitwise NOT complement) */
    int step2 = param2 ^ 0xFF;

    /* Step 3: Combine and multiply by 3 */
    int step3 = (step1 + step2) * 3;

    /* Step 4: Reverse param3 as a byte */
    int param3_byte = param3 & 0xFF;
    int reversed_param3 = reverse_byte(param3_byte);

    /* Step 5: Add param4 */
    int temp = step3 + reversed_param3 + param4;

    /* Step 6: Subtract adjustment ((param5 % 3) * 2) */
    int param5_mod = param5 % 3;
    int adjustment = param5_mod * 2;
    int final_value = temp - adjustment;

    return final_value;
}

/*
 * Main — reads parameters, computes secret, outputs result.
 * The default parameters are the hidden constants of this challenge.
 */
int main()
{
    /*
     * Default embedded constants — discovered through disassembly
     * of generated binary. These are NOT plaintext; they are part of
     * the reconstruction formula.
     */
    int default_params[5] = {3456, 7890, 1234, 5678, 9876};

    printf("=== RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret ===\n\n");

    for (int i = 0; i < 5; i++) {
        printf("param%d+1 = %d\n", i, default_params[i]);
    }

    /* Compute and output the reconstructed secret */
    int result = reconstruct_secret(default_params[0], default_params[1],
                                    default_params[2], default_params[3],
                                    default_params[4]);

    printf("\nReconstructed Secret (hex): %08x\n", result);

    /* Verification — maintainer check */
    int expected_value = 0x00018c80;  /* Computed above */
    if (result == expected_value) {
        printf("Secret matches expected value (maintainer verification)\n");
    } else {
        printf("Secret mismatch — Expected 0x00018c80, got %08x\n", result);
        return 1;
    }

    printf("\n==============================================\n");
    printf("RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret — Complete\n");
    printf("==============================================\n");
    return 0;
}