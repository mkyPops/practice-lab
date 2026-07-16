// first_last_occurrence.cpp
// Demonstrates lower-bound and upper-bound style binary search to find the
// first and last occurrence of a target value in a sorted vector.

#include <iostream>
#include <vector>
#include <utility>

// Returns the index of the first element >= target (lower_bound behavior).
// If no such element exists, returns vec.size().
int lowerBound(const std::vector<int>& vec, int target) {
    int lo = 0, hi = static_cast<int>(vec.size());
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (vec[mid] < target)
            lo = mid + 1;
        else
            hi = mid;
    }
    return lo;
}

// Returns the index of the first element > target (upper_bound behavior).
// If no such element exists, returns vec.size().
int upperBound(const std::vector<int>& vec, int target) {
    int lo = 0, hi = static_cast<int>(vec.size());
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (vec[mid] <= target)
            lo = mid + 1;
        else
            hi = mid;
    }
    return lo;
}

// Finds the first and last index of target in a sorted vector.
// Returns {-1, -1} if target is not present.
std::pair<int, int> findFirstAndLast(const std::vector<int>& vec, int target) {
    int first = lowerBound(vec, target);
    if (first == static_cast<int>(vec.size()) || vec[first] != target) {
        return {-1, -1};
    }
    int last = upperBound(vec, target) - 1;
    return {first, last};
}

int main() {
    std::vector<int> data = {1, 2, 2, 2, 3, 4, 4, 5, 6, 6, 6, 6, 9};

    std::vector<int> queries = {2, 4, 6, 7, 1, 9};
    for (int target : queries) {
        auto [first, last] = findFirstAndLast(data, target);
        if (first == -1) {
            std::cout << "Value " << target << " not found.\n";
        } else {
            std::cout << "Value " << target << " found at indices ["
                      << first << ", " << last << "]\n";
        }
    }

    return 0;
}
