#!/usr/bin/env python3
"""Reference solver for RECOVERED ARTIFACT 2 — derive the key by inverting its validator."""
from __future__ import annotations

SALT = [0x31, 0xA7, 0x5C, 0xD2, 0x48, 0x9E, 0x13, 0xE4,
        0x76, 0x2B, 0xC1, 0x54, 0x8D, 0x3F, 0xB0, 0x69]
EXPECTED = [0xCA, 0xBF, 0x70, 0x79, 0x21, 0xB5, 0xF8, 0xA6,
            0x44, 0xC0, 0x1D, 0x18, 0x7E, 0x67, 0x9C, 0x90]


def rotr8(value: int, count: int) -> int:
    return ((value >> count) | (value << (8 - count))) & 0xFF


def derive_key() -> str:
    # Validator: expected[i] = rotl8(candidate[i] ^ salt[i], (i % 5) + 1)
    # Invert rotation, then XOR with the same per-byte salt.
    return ''.join(chr(rotr8(encoded, (index % 5) + 1) ^ SALT[index])
                   for index, encoded in enumerate(EXPECTED))


if __name__ == '__main__':
    key = derive_key()
    print('Derived recovery key:', key)
    print('Length:', len(key))
    print('Use: printf %s "' + key + '" | ./artifact2_binary')
