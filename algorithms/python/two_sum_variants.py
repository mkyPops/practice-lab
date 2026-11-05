#!/usr/bin/env python3
"""
two_sum_three_sum.py

Implements two classic array algorithms:

- two_sum: finds indices of two numbers in a list that add up to a target,
  using a hash map for O(n) time complexity.
- three_sum: finds all unique triplets in a list that sum to zero,
  using sorting plus the two-pointer technique for O(n^2) time complexity.
"""

from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Return indices (i, j) such that nums[i] + nums[j] == target, or None."""
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return seen[complement], i
        seen[num] = i
    return None


def three_sum(nums: List[int]) -> List[List[int]]:
    """Return all unique triplets [a, b, c] from nums such that a + b + c == 0."""
    nums = sorted(nums)
    n = len(nums)
    result: List[List[int]] = []

    for i in range(n - 2):
        # Skip duplicate values for the first element to avoid duplicate triplets.
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # Smallest possible sum is already positive; no further triplets possible.
        if nums[i] > 0:
            break

        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # Skip duplicates for the second and third elements.
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1

    return result


def _demo() -> None:
    nums = [2, 7, 11, 15]
    target = 9
    print(f"two_sum({nums}, {target}) = {two_sum(nums, target)}")

    triplet_nums = [-1, 0, 1, 2, -1, -4]
    print(f"three_sum({triplet_nums}) = {three_sum(triplet_nums)}")


if __name__ == "__main__":
    _demo()
