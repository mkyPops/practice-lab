"""
Two Sum and Three Sum algorithms.

- two_sum: finds indices of two numbers in a list that add up to a target,
  using a hash map for O(n) time complexity.
- three_sum: finds all unique triplets in a list that sum to zero,
  using sorting plus a two-pointer technique for O(n^2) time complexity.
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
    result = []

    for i in range(n - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Small optimizations: smallest possible sum > 0 means no more solutions
        if nums[i] + nums[i + 1] + nums[i + 2] > 0:
            break
        # Largest possible sum < 0 means this i can't work, move on
        if nums[i] + nums[n - 2] + nums[n - 1] < 0:
            continue

        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # Skip duplicates for second and third elements
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result


if __name__ == "__main__":
    sample = [2, 7, 11, 15]
    print("Two Sum:", two_sum(sample, 9))

    triplets_input = [-1, 0, 1, 2, -1, -4]
    print("Three Sum:", three_sum(triplets_input))
