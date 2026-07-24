// MinHeap.java
// A generic binary min-heap backed by a dynamically resizing array.
// Supports insertion, peeking, and extraction of the minimum element
// in O(log n) time using sift-up and sift-down operations.

import java.util.Arrays;
import java.util.NoSuchElementException;

public class MinHeap<T extends Comparable<T>> {
    private Object[] elements;
    private int size;

    public MinHeap() {
        this(16);
    }

    public MinHeap(int initialCapacity) {
        elements = new Object[Math.max(initialCapacity, 1)];
        size = 0;
    }

    public int size() {
        return size;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public void insert(T value) {
        if (value == null) {
            throw new NullPointerException("value cannot be null");
        }
        ensureCapacity();
        elements[size] = value;
        siftUp(size);
        size++;
    }

    public T peek() {
        if (isEmpty()) {
            throw new NoSuchElementException("heap is empty");
        }
        return elementAt(0);
    }

    public T extractMin() {
        T min = peek();
        size--;
        elements[0] = elements[size];
        elements[size] = null;
        siftDown(0);
        return min;
    }

    private void siftUp(int index) {
        while (index > 0) {
            int parent = (index - 1) / 2;
            if (elementAt(index).compareTo(elementAt(parent)) >= 0) {
                break;
            }
            swap(index, parent);
            index = parent;
        }
    }

    private void siftDown(int index) {
        while (true) {
            int left = 2 * index + 1;
            int right = 2 * index + 2;
            int smallest = index;

            if (left < size && elementAt(left).compareTo(elementAt(smallest)) < 0) {
                smallest = left;
            }
            if (right < size && elementAt(right).compareTo(elementAt(smallest)) < 0) {
                smallest = right;
            }
            if (smallest == index) {
                break;
            }
            swap(index, smallest);
            index = smallest;
        }
    }

    private void ensureCapacity() {
        if (size == elements.length) {
            elements = Arrays.copyOf(elements, elements.length * 2);
        }
    }

    private void swap(int i, int j) {
        Object tmp = elements[i];
        elements[i] = elements[j];
        elements[j] = tmp;
    }

    @SuppressWarnings("unchecked")
    private T elementAt(int index) {
        return (T) elements[index];
    }
}
