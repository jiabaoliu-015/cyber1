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

PARAMETERS (embedded constants in binary — discovered through disassembly):
  param1 = 3456
  param2 = 7890
  param3 = 1234
  param4 = 5678
  param5 = 9876

EXPECTED OUTPUT: 0x00018c80 (8-digit hex format; 4-character digest)

This solver verifies the reconstruction matches the expected secret.
"""

import sys


def reverse_byte(byte_value: int) -> int:
    """
    Reverse the bits of a byte — same operation as in the C binary.
    This is a simple bit-reversal for educational clarity.
    """
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
    # Step 1: Multiply param1 by 7
    step1 = param1 * 7
    
    # Step 2: XOR param2 with 0xFF
    step2 = param2 ^ 0xFF
    
    # Step 3: Add then multiply by 3
    step3 = (step1 + step2) * 3
    
    # Step 4: Reverse param3 as a byte (only last byte of param3 used)
    param3_byte = param3 & 0xFF
    reversed_param3 = reverse_byte(param3_byte)
    
    # Step 5: Add param4
    temp = step3 + reversed_param3 + param4
    
    # Step 6: Subtract ((param5 % 3) * 2)
    param5_mod = param5 % 3
    adjustment = param5_mod * 2
    final_value = temp - adjustment
    
    return final_value


def verify_parameters():
    """
    Verify that the parameters produce the expected hex digest.
    
    This confirms the solver correctly implements the discovered algorithm.
    """
    # These are the constants embedded in the binary, discovered through
    # disassembly analysis of the C source / objdump output.
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
    
    result = reconstruct_secret(param1, param2, param3, param4, param5)
    
    print("ALGORITHM RECONSTRUCTION:")
    print("  step1    = param1 * 7      = " + str(param1 * 7))
    print("  step2    = param2 ^ 0xFF    = " + str(param2 ^ 0xFF))
    print("  step3    = (step1 + step2) * 3 = " + str((param1*7 + param2^0xFF) * 3))
    print("  reverse_byte(param3 & 0xFF) = " + str(reverse_byte(param3 & 0xFF)))
    print("  temp     = step3 + reverse + param4 = " + str(result + param5 % 3) + " + " + str(param4))
    param5_mod = param5 % 3
    adjustment = param5_mod * 2
    print("  adjustment = (param5 % 3) * 2 = " + str(param5_mod) + "*2")
    print()
    print(f"RESULT: {result}")
    print(f"FORMAT: {result:08x}")
    print()
    
    if result == expected:
        print(f"[OK] Secret matches expected value: 0x{result:08x}")
        return True
    else:
        print(f"[ERROR] Secret mismatch — Expected 0x{expected:08x}, got 0x{result:08x}")
        return False


def what_strings_finds():
    """
    Demonstrate what strings alone discovers compared to the full algorithm.
    """
    print("\n" + "=" * 70)
    print(" WHAT `strings` ALONE CAN FIND:")
    print("-" * 70)
    print("  The binary contains strings like:")
    print("    '=== RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret ==='")
    print("    'Reconstructed Secret (hex):'")
    print("  But these are NOT the secret value — they are just labels.")
    print()
    print("  The ACTUAL secret value is computed at runtime from constants")
    print("  embedded in the code (param1 through param5).")
    print()
    print("  This demonstrates: strings finds labels, but disassembly reveals")
    print("  the computation that generates the real value.")
    
    # Compute what the algorithm produces
    params = [3456, 7890, 1234, 5678, 9876]
    param1, param2, param3, param4, param5 = params
    result = reconstruct_secret(param1, param2, param3, param4, param5)
    print()
    print("=" * 70)
    print(" THE REAL SECRET VALUE (computed, not in strings):")
    print(f"  0x{result:08x}")
    print("=" * 70)


def main():
    # Show what strings finds vs the computed value
    what_strings_finds()
    
    # Verify the solver's algorithm
    success = verify_parameters()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()