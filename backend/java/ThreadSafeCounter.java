/*
 * ThreadSafeCounter.java
 *
 * A thread-safe counter implementation backed by AtomicLong.
 * Supports increment, decrement, reset, and compare-and-swap (CAS)
 * operations without explicit locking, relying on atomic hardware
 * instructions for consistency under concurrent access.
 */

import java.util.concurrent.atomic.AtomicLong;

public final class ThreadSafeCounter {

    private final AtomicLong value = new AtomicLong(0L);

    /** Increments the counter by 1 and returns the updated value. */
    public long increment() {
        return value.incrementAndGet();
    }

    /** Decrements the counter by 1 and returns the updated value. */
    public long decrement() {
        return value.decrementAndGet();
    }

    /** Adds the given delta (may be negative) and returns the updated value. */
    public long add(long delta) {
        return value.addAndGet(delta);
    }

    /** Resets the counter to zero and returns the previous value. */
    public long reset() {
        return value.getAndSet(0L);
    }

    /** Returns the current value of the counter. */
    public long get() {
        return value.get();
    }

    /**
     * Atomically sets the value to {@code newValue} if the current value
     * equals {@code expectedValue}.
     *
     * @return true if the update was successful, false otherwise
     */
    public boolean compareAndSwap(long expectedValue, long newValue) {
        return value.compareAndSet(expectedValue, newValue);
    }

    /** Simple demonstration of concurrent usage. */
    public static void main(String[] args) throws InterruptedException {
        ThreadSafeCounter counter = new ThreadSafeCounter();
        int threadCount = 10;
        int incrementsPerThread = 1000;

        Runnable task = () -> {
            for (int i = 0; i < incrementsPerThread; i++) {
                counter.increment();
            }
        };

        Thread[] threads = new Thread[threadCount];
        for (int i = 0; i < threadCount; i++) {
            threads[i] = new Thread(task);
            threads[i].start();
        }
        for (Thread t : threads) {
            t.join();
        }

        System.out.println("Final counter value: " + counter.get());
        System.out.println("CAS 10000 -> 0: " + counter.compareAndSwap(10000, 0));
        System.out.println("Value after CAS: " + counter.get());
    }
}
