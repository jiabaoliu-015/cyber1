#!/usr/bin/env python3
"""
RECOVERED ARTIFACT 1 — Reference Solver (Runtime-Reconstructed Secret)

Demonstrates how to solve RECOVERED ARTIFACT 1 from the algorithm rather than brute force.

SOLVE PATH:
1. Analyze the binary with objdump/readelf to discover the constants
2. Identify the reconstruction algorithm from the assembly instructions
3. Implement the algorithm in Python to compute the secret
4. Verify the output matches the expected value

ALGORITHM (discovered through binary disassembly):
  secret_value = ((param1 * 7) + (param2 ^ 0xFF)) * 3
                + reverse_byte(param3)
                + param4
                - ((param5 % 3) * 2)

PARAMETERS (embedded constants in binary — discovered via disassembly):
  param1 = 3456
  param2 = 7890
  param3 = 1234
  param4 = 5678
  param5 = 9876

EXPECTED OUTPUT: 0x00018c80

This solver verifies the reconstruction matches the expected secret.
"""

import sys


def reverse_byte(byte_value: int) -> int:
    """Reverse the bits of a byte — same operation as in the C binary. Educational clarity."""
    result = 0
    for i in range(8):
        bit = (byte_value >> i) & 1
        result |= bit << (7 - i)
    return result


def reconstruct_secret(param1: int, param2: int, param3: int, param4: int, param5: int) -> int:
    """
    Reconstruct the secret using the runtime algorithm discovered from disassembly.

    Formula: ((param1*7)+(param2^0xFF))*3 + reverse_byte(param3) + param4 - ((param5%3)*2)
    """
    step1 = param1 * 7
    step2 = param2 ^ 0xFF
    step3 = (step1 + step2) * 3
    param3_byte = param3 & 0xFF
    reversed_param3 = reverse_byte(param3_byte)
    temp = step3 + reversed_param3 + param4
    param5_mod = param5 % 3
    adjustment = param5_mod * 2
    final_value = temp - adjustment
    return final_value


def verify_parameters():
    """Verify parameters produce expected hex digest."""
    params = [3456, 7890, 1234, 5678, 9876]
    param1, param2, param3, param4, param5 = params
    expected = 0x00018c80

    print("\n" + "=" * 70)
    print(" RECOVERED ARTIFACT 1 — Reference Solver")
    print(" Reverse-Engineering Solution — Runtime Reconstruction     ")
    print("=" * 70)
    print()
    print("PARAMETERS DISCOVERED THROUGH BINARY ANALYSIS:")
    print(f"  param1    = {param1}")
    print(f"  param2    = {param2}")
    print(f"  param3    = {param3}")
    print(f"  param4    = {param4}")
    print(f"  param5    = {param5}")
    print()

    step1 = param1 * 7
    step2 = param2 ^ 0xFF
    step3 = (step1 + step2) * 3
    rev3 = reverse_byte(param3 & 0xFF)
    param5_mod = param5 % 3
    adjustment = param5_mod * 2

    print("ALGORITHM RECONSTRUCTION STEPS:")
    print(f"  step1    = param1 * 7      = {step1}")
    print(f"  step2    = param2 ^ 0xFF    = {step2}")
    print(f"  step3    = (step1 + step2) * 3 = {step3}")
    print(f"  reverse_byte(param3 & 0xFF) = {rev3}")
    print(f"  param5 % 3 = {param5_mod}")
    print(f"  adjustment = {param5_mod} * 2 = {adjustment}")
    print()

    result = reconstruct_secret(param1, param2, param3, param4, param5)
    print(f"RESULT: {result}")
    print(f"FORMAT: {result:08x}")
    print()

    if result == expected:
        print("[" + "OK" + "] Secret matches expected value: 0x{:08x}".format(result))
        return True
    else:
        print("[ERROR] Secret mismatch — Expected 0x{:08x}, got 0x{:08x}".format(expected, result))
        return False


def what_strings_alone_finds():
    """Demonstrate what strings alone can and cannot find."""
    print("\n" + "=" * 70)
    print(" WHAT `strings` ALONE DISCOVERS IN THE BINARY:")
    print("-" * 70)
    print("  Label strings found (NOT the secret value):")
    print("    '=== RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret ==='")
    print("    'Reconstructed Secret (hex):'")
    print("    'param1+1 = ...' labels")
    print()
    print("  CONCLUSION: strings reveals INTERFACE LABELS, NOT THE VALUE.")
    print("  The actual secret value is computed at runtime via embedded constants.")
    print()
    print("=" * 70)
    
    # Compute the actual value
    params = [3456, 7890, 1234, 5678, 9876]
    param1, param2, param3, param4, param5 = params
    result = reconstruct_secret(param1, param2, param3, param4, param5)
    print("=" * 70)
    print(" THE REAL SECRET VALUE (computed at runtime):")
    print(f"  0x{result:08x}")
    print("=" * 70)


def main():
    what_strings_alone_finds()
    success = verify_parameters()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())