/*
 * Producer-Consumer demo using a LinkedBlockingQueue.
 * Multiple producer threads generate integer items and place them on a
 * shared bounded queue; multiple consumer threads take items and process
 * them. Shutdown is coordinated with "poison pill" sentinel values: once
 * all producers finish, one poison pill per consumer is enqueued so each
 * consumer can exit cleanly after draining remaining work.
 */
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ProducerConsumerDemo {

    private static final int QUEUE_CAPACITY = 20;
    private static final int NUM_PRODUCERS = 3;
    private static final int NUM_CONSUMERS = 4;
    private static final int ITEMS_PER_PRODUCER = 10;

    // Sentinel value signaling a consumer should stop.
    private static final Integer POISON_PILL = Integer.MIN_VALUE;

    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);
        ExecutorService producerPool = Executors.newFixedThreadPool(NUM_PRODUCERS);
        ExecutorService consumerPool = Executors.newFixedThreadPool(NUM_CONSUMERS);
        AtomicInteger itemSequence = new AtomicInteger(0);

        // Launch producers.
        for (int p = 0; p < NUM_PRODUCERS; p++) {
            producerPool.submit(() -> {
                try {
                    for (int i = 0; i < ITEMS_PER_PRODUCER; i++) {
                        int item = itemSequence.incrementAndGet();
                        queue.put(item);
                        System.out.println(Thread.currentThread().getName() + " produced " + item);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }

        // Launch consumers.
        for (int c = 0; c < NUM_CONSUMERS; c++) {
            consumerPool.submit(() -> {
                try {
                    while (true) {
                        Integer item = queue.take();
                        if (item.equals(POISON_PILL)) {
                            break; // stop signal received
                        }
                        System.out.println(Thread.currentThread().getName() + " consumed " + item);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }

        producerPool.shutdown();
        producerPool.awaitTermination(1, TimeUnit.MINUTES);

        // All production done; enqueue one poison pill per consumer.
        for (int c = 0; c < NUM_CONSUMERS; c++) {
            queue.put(POISON_PILL);
        }

        consumerPool.shutdown();
        consumerPool.awaitTermination(1, TimeUnit.MINUTES);

        System.out.println("All producers and consumers have finished.");
    }
}
