"""
Sliding Window Maximum

Computes the maximum value in every contiguous sliding window of size k
across a list of numbers, using a monotonic deque to achieve O(n) time
complexity (each element is pushed and popped from the deque at most once).
"""

from collections import deque
from typing import List


def sliding_window_maximum(nums: List[int], k: int) -> List[int]:
    """Return a list of maximums for each sliding window of size k.

    Args:
        nums: List of numbers to scan.
        k: Size of the sliding window (must be a positive integer <= len(nums)).

    Returns:
        A list containing the maximum of each window, in order.
    """
    if not nums or k <= 0:
        return []
    if k > len(nums):
        raise ValueError("Window size k cannot exceed the length of nums")

    result = []
    # Deque stores indices into nums; values are kept in decreasing order.
    window: deque = deque()

    for i, num in enumerate(nums):
        # Remove indices that have slid out of the current window.
        if window and window[0] <= i - k:
            window.popleft()

        # Maintain decreasing order: drop smaller values from the back,
        # since they can never be the max while num is still in range.
        while window and nums[window[-1]] <= num:
            window.pop()

        window.append(i)

        # Once we've processed at least k elements, record the max.
        if i >= k - 1:
            result.append(nums[window[0]])

    return result


if __name__ == "__main__":
    sample = [1, 3, -1, -3, 5, 3, 6, 7]
    window_size = 3
    print(f"Input: {sample}, k={window_size}")
    print(f"Sliding window maximums: {sliding_window_maximum(sample, window_size)}")
