import java.util.EmptyStackException;

/**
 * A generic, array-backed stack implementation with dynamic resizing.
 * The backing array doubles in capacity when full and halves in capacity
 * when usage drops to one quarter of the capacity, keeping memory usage
 * proportional to the number of elements stored.
 */
public class Stack<T> {

    private static final int DEFAULT_CAPACITY = 8;

    private Object[] data;
    private int size;

    public Stack() {
        data = new Object[DEFAULT_CAPACITY];
        size = 0;
    }

    public void push(T item) {
        if (size == data.length) {
            resize(data.length * 2);
        }
        data[size++] = item;
    }

    @SuppressWarnings("unchecked")
    public T pop() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        T item = (T) data[--size];
        data[size] = null; // avoid memory leak by clearing the reference

        // Shrink when usage falls to a quarter, but never below default capacity.
        if (size > 0 && size == data.length / 4 && data.length / 2 >= DEFAULT_CAPACITY) {
            resize(data.length / 2);
        }
        return item;
    }

    @SuppressWarnings("unchecked")
    public T peek() {
        if (isEmpty()) {
            throw new EmptyStackException();
        }
        return (T) data[size - 1];
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public int size() {
        return size;
    }

    private void resize(int newCapacity) {
        Object[] newData = new Object[newCapacity];
        System.arraycopy(data, 0, newData, 0, size);
        data = newData;
    }
}
