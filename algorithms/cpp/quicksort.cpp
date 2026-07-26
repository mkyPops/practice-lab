// quicksort.cpp
// In-place quicksort using median-of-three pivot selection to avoid
// worst-case O(n^2) behavior on already-sorted or reverse-sorted input.

#include <iostream>
#include <vector>
#include <utility>

// Chooses the median of arr[low], arr[mid], arr[high] as the pivot,
// moves it to arr[high - 1], and returns its index.
template <typename T>
int medianOfThree(std::vector<T>& arr, int low, int high) {
    int mid = low + (high - low) / 2;

    if (arr[mid] < arr[low])
        std::swap(arr[mid], arr[low]);
    if (arr[high] < arr[low])
        std::swap(arr[high], arr[low]);
    if (arr[high] < arr[mid])
        std::swap(arr[high], arr[mid]);

    // arr[mid] now holds the median value; stash it just before arr[high]
    // so it can act as the pivot for Hoare-style partitioning.
    std::swap(arr[mid], arr[high - 1]);
    return high - 1;
}

// Partitions arr[low..high] around the pivot placed at high - 1.
template <typename T>
int partition(std::vector<T>& arr, int low, int high) {
    int pivotIndex = medianOfThree(arr, low, high);
    T pivotValue = arr[pivotIndex];

    int i = low;
    int j = high - 1;

    while (true) {
        while (arr[++i] < pivotValue) {}
        while (pivotValue < arr[--j]) {}
        if (i >= j) break;
        std::swap(arr[i], arr[j]);
    }

    // Restore pivot to its final sorted position.
    std::swap(arr[i], arr[high - 1]);
    return i;
}

template <typename T>
void quicksort(std::vector<T>& arr, int low, int high) {
    // Use insertion sort for small partitions to reduce overhead.
    const int kInsertionThreshold = 16;

    if (high - low + 1 <= kInsertionThreshold) {
        for (int i = low + 1; i <= high; ++i) {
            T key = arr[i];
            int k = i - 1;
            while (k >= low && arr[k] > key) {
                arr[k + 1] = arr[k];
                --k;
            }
            arr[k + 1] = key;
        }
        return;
    }

    int pivotIndex = partition(arr, low, high);
    quicksort(arr, low, pivotIndex - 1);
    quicksort(arr, pivotIndex + 1, high);
}

template <typename T>
void quicksort(std::vector<T>& arr) {
    if (arr.size() > 1)
        quicksort(arr, 0, static_cast<int>(arr.size()) - 1);
}

int main() {
    std::vector<int> data = {9, 3, 7, 1, 8, 2, 5, 4, 6, 0, 10, 12, 11, -3, -1};

    quicksort(data);

    for (size_t i = 0; i < data.size(); ++i) {
        std::cout << data[i] << (i + 1 < data.size() ? ' ' : '\n');
    }

    // Additional check on already-sorted input to demonstrate resilience
    // against worst-case behavior.
    std::vector<int> sortedInput;
    for (int i = 0; i < 1000; ++i) sortedInput.push_back(i);
    quicksort(sortedInput);

    bool ok = true;
    for (size_t i = 1; i < sortedInput.size(); ++i) {
        if (sortedInput[i - 1] > sortedInput[i]) {
            ok = false;
            break;
        }
    }
    std::cout << (ok ? "Sorted correctly.\n" : "Sort failed.\n");

    return 0;
}
