"""
Sliding Window Maximum

Given an array of integers and a window size k, this module computes the
maximum value within each contiguous sliding window of size k as it moves
from left to right across the array. Uses a monotonic deque of indices to
achieve O(n) time complexity overall.
"""

from collections import deque
from typing import List


def sliding_window_maximum(nums: List[int], k: int) -> List[int]:
    """Return a list of maximums for each sliding window of size k."""
    if not nums or k <= 0:
        return []
    if k > len(nums):
        raise ValueError("Window size k cannot exceed the length of nums")

    result = []
    dq = deque()  # will store indices of nums, values in decreasing order

    for i, num in enumerate(nums):
        # Remove indices that are out of the current window's bounds
        if dq and dq[0] <= i - k:
            dq.popleft()

        # Remove indices whose values are smaller than the current number,
        # since they can never be the maximum while num is in the window
        while dq and nums[dq[-1]] < num:
            dq.pop()

        dq.append(i)

        # The front of the deque is the index of the current window's max
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


if __name__ == "__main__":
    sample = [1, 3, -1, -3, 5, 3, 6, 7]
    window_size = 3
    print(f"Array: {sample}")
    print(f"Window size: {window_size}")
    print(f"Sliding window maximums: {sliding_window_maximum(sample, window_size)}")
