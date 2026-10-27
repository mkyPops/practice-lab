#!/usr/bin/env python3
"""
Bloom filter implementation.

A space-efficient probabilistic data structure for approximate set
membership testing. False positives are possible, false negatives are not:
if `contains` returns False, the item was definitely never added; if it
returns True, the item was probably added.
"""

import hashlib
import math


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be between 0 and 1")

        # Optimal bit array size: m = -n * ln(p) / (ln(2)^2)
        self.size = max(1, math.ceil(
            -expected_items * math.log(false_positive_rate) / (math.log(2) ** 2)
        ))
        # Optimal number of hash functions: k = (m/n) * ln(2)
        self.hash_count = max(1, round((self.size / expected_items) * math.log(2)))

        self.bit_array = bytearray((self.size + 7) // 8)
        self.item_count = 0

    def _hashes(self, item: str):
        # Derive `hash_count` independent-ish indices from two base hashes
        # using the double hashing technique (Kirsch-Mitzenmacher).
        data = item.encode("utf-8")
        h1 = int.from_bytes(hashlib.sha256(data).digest()[:8], "big")
        h2 = int.from_bytes(hashlib.md5(data).digest()[:8], "big")
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        for index in self._hashes(item):
            self.bit_array[index // 8] |= 1 << (index % 8)
        self.item_count += 1

    def contains(self, item: str) -> bool:
        return all(
            self.bit_array[index // 8] & (1 << (index % 8))
            for index in self._hashes(item)
        )

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def estimated_false_positive_rate(self) -> float:
        # p ≈ (1 - e^(-k*n/m))^k
        exponent = -self.hash_count * self.item_count / self.size
        return (1 - math.exp(exponent)) ** self.hash_count


if __name__ == "__main__":
    bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)

    words = ["apple", "banana", "cherry", "date", "elderberry"]
    for word in words:
        bf.add(word)

    for word in words:
        assert word in bf, f"{word} should be present"

    print("All inserted items detected as present.")
    print("date" in bf, "grape" in bf)
    print(f"Estimated false positive rate: {bf.estimated_false_positive_rate():.4f}")
