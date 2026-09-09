"""
Bloom filter implementation.

A space-efficient probabilistic set membership structure. Supports insertion
and membership queries with a tunable false-positive rate; false negatives
never occur. Uses double hashing (two independent hash functions combined
linearly) to simulate k independent hash functions efficiently.
"""

import hashlib
import math


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not (0 < false_positive_rate < 1):
            raise ValueError("false_positive_rate must be between 0 and 1")

        # Optimal bit array size: m = -(n * ln(p)) / (ln(2)^2)
        self.size = max(1, math.ceil(
            -(expected_items * math.log(false_positive_rate)) / (math.log(2) ** 2)
        ))
        # Optimal number of hash functions: k = (m/n) * ln(2)
        self.num_hashes = max(1, round((self.size / expected_items) * math.log(2)))
        self.bit_array = bytearray((self.size + 7) // 8)
        self.count = 0

    def _hashes(self, item: str):
        # Derive two base hashes from md5/sha1 digests, then combine them
        # (double hashing) to cheaply generate num_hashes indices.
        item_bytes = str(item).encode("utf-8")
        h1 = int.from_bytes(hashlib.md5(item_bytes).digest()[:8], "big")
        h2 = int.from_bytes(hashlib.sha1(item_bytes).digest()[:8], "big")

        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        for index in self._hashes(item):
            byte_index, bit_offset = divmod(index, 8)
            self.bit_array[byte_index] |= (1 << bit_offset)
        self.count += 1

    def __contains__(self, item: str) -> bool:
        for index in self._hashes(item):
            byte_index, bit_offset = divmod(index, 8)
            if not (self.bit_array[byte_index] & (1 << bit_offset)):
                return False
        return True

    def current_false_positive_rate(self) -> float:
        # Estimate based on actual number of items inserted so far.
        exponent = -self.num_hashes * self.count / self.size
        return (1 - math.exp(exponent)) ** self.num_hashes


if __name__ == "__main__":
    bloom = BloomFilter(expected_items=1000, false_positive_rate=0.01)
    words = ["apple", "banana", "cherry", "date", "elderberry"]

    for word in words:
        bloom.add(word)

    for word in words:
        assert word in bloom  # no false negatives

    print("grape" in bloom)  # likely False, possibly a false positive
    print(f"Estimated false positive rate: {bloom.current_false_positive_rate():.4%}")
