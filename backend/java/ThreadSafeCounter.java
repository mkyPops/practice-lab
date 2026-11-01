/*
 * ThreadSafeCounter.java
 *
 * A simple thread-safe counter backed by AtomicLong.
 * Supports increment, decrement, reset, and a compare-and-swap (CAS) operation.
 * Demonstrates usage with multiple concurrent threads in main().
 */

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public final class ThreadSafeCounter {

    private final AtomicLong value = new AtomicLong(0L);

    /** Atomically increments the counter by one and returns the new value. */
    public long increment() {
        return value.incrementAndGet();
    }

    /** Atomically decrements the counter by one and returns the new value. */
    public long decrement() {
        return value.decrementAndGet();
    }

    /** Resets the counter to zero and returns the previous value. */
    public long reset() {
        return value.getAndSet(0L);
    }

    /** Returns the current value. */
    public long get() {
        return value.get();
    }

    /**
     * Atomically sets the value to {@code update} if the current value equals
     * {@code expected}. Returns true on success, false otherwise.
     */
    public boolean compareAndSwap(long expected, long update) {
        return value.compareAndSet(expected, update);
    }

    public static void main(String[] args) throws InterruptedException {
        ThreadSafeCounter counter = new ThreadSafeCounter();
        ExecutorService pool = Executors.newFixedThreadPool(4);

        // Launch 1000 increments and 500 decrements concurrently.
        for (int i = 0; i < 1000; i++) {
            pool.submit(counter::increment);
        }
        for (int i = 0; i < 500; i++) {
            pool.submit(counter::decrement);
        }

        pool.shutdown();
        pool.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("Final value (expected 500): " + counter.get());

        // Demonstrate CAS: only succeeds if current value matches expected.
        boolean success = counter.compareAndSwap(500L, 42L);
        System.out.println("CAS success: " + success + ", value now: " + counter.get());

        counter.reset();
        System.out.println("After reset: " + counter.get());
    }
}
