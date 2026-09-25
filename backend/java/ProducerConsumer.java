/*
 * Producer-Consumer demo using a LinkedBlockingQueue as the shared buffer.
 * Multiple producer threads generate integer items and place them on the
 * queue; multiple consumer threads take and process them concurrently.
 * A sentinel "poison pill" value is used to signal consumers to stop once
 * all producers have finished.
 */
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;

public class ProducerConsumerDemo {

    private static final int NUM_PRODUCERS = 3;
    private static final int NUM_CONSUMERS = 2;
    private static final int ITEMS_PER_PRODUCER = 5;
    private static final Integer POISON_PILL = Integer.MIN_VALUE;

    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(10);
        AtomicInteger producedCounter = new AtomicInteger(0);

        Thread[] producers = new Thread[NUM_PRODUCERS];
        for (int p = 0; p < NUM_PRODUCERS; p++) {
            int producerId = p;
            producers[p] = new Thread(() -> {
                for (int i = 0; i < ITEMS_PER_PRODUCER; i++) {
                    int value = producerId * 1000 + i;
                    try {
                        queue.put(value); // blocks if queue is full
                        System.out.println("Producer " + producerId + " produced " + value);
                        producedCounter.incrementAndGet();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
            }, "producer-" + p);
            producers[p].start();
        }

        Thread[] consumers = new Thread[NUM_CONSUMERS];
        for (int c = 0; c < NUM_CONSUMERS; c++) {
            int consumerId = c;
            consumers[c] = new Thread(() -> {
                try {
                    while (true) {
                        Integer item = queue.take(); // blocks if queue is empty
                        if (item.equals(POISON_PILL)) {
                            queue.put(POISON_PILL); // pass the pill along for other consumers
                            break;
                        }
                        System.out.println("Consumer " + consumerId + " consumed " + item);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "consumer-" + c);
            consumers[c].start();
        }

        // Wait for all producers to finish before signaling consumers to stop.
        for (Thread producer : producers) {
            producer.join();
        }
        queue.put(POISON_PILL); // triggers the relay chain among consumers

        for (Thread consumer : consumers) {
            consumer.join();
        }

        System.out.println("Total items produced: " + producedCounter.get());
        System.out.println("All producers and consumers have finished.");
    }
}
