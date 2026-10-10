#!/usr/bin/env python3
"""
RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret

Reverse Engineering Challenge: Runtime Secret Reconstruction

Description:
The binary reconstructs a secret/credential at runtime through a series of
simple mathematical and bitwise operations — NOT stored as obvious plaintext.

Reconstruction Formula:
  secret = ((param1 * 7) + (param2 XOR 0xFF)) * 3 + (param3_reversed_as_byte) + param4 - ((param5 % 3) * 2)

Output: A string representation of the computed result

Intended Tools: strings, objdump, readelf, nm (ordinary reversing tools)
Learning Objective: Understanding runtime computation patterns in compiled binaries

Player Discovery Path:
1. Run the binary and observe how it transforms inputs
2. Use `strings` to see if values leak — but they won't be plaintext
3. Disassemble with `objdump/readelf` to reverse-engineer the computation
4. Reconstruct the algorithm and determine the input that yields the valid credential

Reset Behavior: The binary outputs the reconstructed secret — no side effects required.

Notes:
- The transformation is simple enough for a student to explain during the demo
- Deterministic output on every run
- No extreme obfuscation or brute-force requirements
"""

import sys
import struct
import os

ROOT_FLAG = "CITS3006_ROOT_FLAG"
PROJECT_ROOT = "/home/kali/Desktop/CITS3006-Project"
D_DIR = os.path.join(PROJECT_ROOT, "labs/offline-artefact-lab/challenges")


def reconstruct_secret(param1: int, param2: int, param3: int, param4: int, param5: int) -> str:
    """
    Reconstruct the secret using the runtime algorithm:
    
    secret_value = ((param1 * 7) + (param2 XOR 0xFF)) * 3 + (param3 reversed as byte) + param4 - ((param5 % 3) * 2)
    
    Then converts to a string representation.
    """
    # Step 1: Multiply param1 by 7
    step1 = param1 * 7
    
    # Step 2: XOR param2 with 0xFF (bitwise NOT complement)
    step2 = param2 ^ 0xFF
    
    # Step 3: Add then multiply by 3
    step3 = (step1 + step2) * 3
    
    # Step 4: Reverse param3 as a byte (simple bit reversal for educational clarity)
    param3_byte = param3 & 0xFF
    reversed_param3 = reverse_byte(param3_byte)
    
    # Step 5: Add param4
    temp = step3 + param4
    
    # Step 6: Subtract ((param5 % 3) * 2)
    param5_mod = param5 % 3
    adjustment = param5_mod * 2
    
    final_value = temp - adjustment
    
    # Convert to string — the reconstructed credential
    return f"{final_value:04x}"  # 4-character hex digest representing the secret


def reverse_byte(byte_value: int) -> int:
    """
    Reverse the bits of a byte for educational purposes in this challenge.
    Simple bit-reversal operation — demonstrates understanding of operations.
    """
    result = 0
    for i in range(8):
        bit = (byte_value >> i) & 1
        result |= bit << (7 - i)
    return result


def main():
    """
    Entry point — reads parameters, computes secret, outputs result.
    Designed to be compiled to a native binary for reverse engineering practice.
    """
    # Default parameters for testing/verification (hidden from strings output in compiled binary)
    # The player must discover these through analysis
    default_params = (73, 101, 45, 89, 23)
    
    params = default_params
    
    for i, param in enumerate(params):
        if i < 5:
            print(f"param{i+1} = {param}")
    
    # Reconstruct the secret using the algorithm
    secret_value = reconstruct_secret(*params)
    
    # Display the reconstructed secret
    print(f"\nReconstructed Secret: {secret_value}")
    
    # Verify against expected output (for maintainer testing)
    expected = "f0a3c7d1"
    if secret_value == expected:
        print("\n✓ Secret matches expected value (maintainer verification)")
    else:
        print(f"\n✗ Secret mismatch — Expected '{expected}', got '{secret_value}'")
        sys.exit(1)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())