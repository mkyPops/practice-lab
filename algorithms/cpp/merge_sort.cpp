// merge_sort.cpp
// A stable merge sort implementation over std::vector<T>.
// The merge step is factored into its own function for clarity and reuse.

#include <vector>
#include <iostream>
#include <algorithm>

// Merges two contiguous, already-sorted subranges [left, mid) and [mid, right)
// of `data` into a single sorted range, using `buffer` as scratch space.
// Stability is preserved by preferring the left element on ties.
template <typename T>
void merge(std::vector<T>& data, std::vector<T>& buffer,
           std::size_t left, std::size_t mid, std::size_t right) {
    std::size_t i = left;
    std::size_t j = mid;
    std::size_t k = left;

    while (i < mid && j < right) {
        if (data[i] <= data[j]) {
            buffer[k++] = data[i++];
        } else {
            buffer[k++] = data[j++];
        }
    }
    // Copy any remaining elements from whichever side still has some.
    while (i < mid)   buffer[k++] = data[i++];
    while (j < right) buffer[k++] = data[j++];

    // Write merged results back into the original range.
    for (std::size_t idx = left; idx < right; ++idx) {
        data[idx] = buffer[idx];
    }
}

// Recursively sorts data[left, right) using merge sort.
template <typename T>
void merge_sort_impl(std::vector<T>& data, std::vector<T>& buffer,
                      std::size_t left, std::size_t right) {
    if (right - left <= 1) {
        return; // Zero or one element: already sorted.
    }
    std::size_t mid = left + (right - left) / 2;
    merge_sort_impl(data, buffer, left, mid);
    merge_sort_impl(data, buffer, mid, right);
    merge(data, buffer, left, mid, right);
}

// Public entry point: stable merge sort over a vector.
template <typename T>
void merge_sort(std::vector<T>& data) {
    if (data.size() < 2) {
        return;
    }
    std::vector<T> buffer(data.size());
    merge_sort_impl(data, buffer, 0, data.size());
}

int main() {
    std::vector<int> nums = {9, 3, 7, 3, 1, 8, 2, 3, 5, 0};

    merge_sort(nums);

    for (int n : nums) {
        std::cout << n << ' ';
    }
    std::cout << '\n';

    return 0;
}
