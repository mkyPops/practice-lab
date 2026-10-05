/*
 * LRUCache.java
 *
 * A generic Least-Recently-Used (LRU) cache implementation backed by a
 * LinkedHashMap configured in access-order mode. Both get() and put()
 * run in amortized O(1) time, since LinkedHashMap maintains a doubly
 * linked list of entries alongside its hash table to track ordering,
 * and eviction of the eldest entry is handled automatically by
 * overriding removeEldestEntry().
 */

import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache<K, V> {

    private final int capacity;
    private final LinkedHashMap<K, V> map;

    public LRUCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        this.capacity = capacity;
        // accessOrder=true reorders entries on get/put so the eldest entry
        // is always the least recently used one.
        this.map = new LinkedHashMap<K, V>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > LRUCache.this.capacity;
            }
        };
    }

    public synchronized V get(K key) {
        return map.get(key);
    }

    public synchronized void put(K key, V value) {
        map.put(key, value);
    }

    public synchronized boolean containsKey(K key) {
        return map.containsKey(key);
    }

    public synchronized int size() {
        return map.size();
    }

    @Override
    public synchronized String toString() {
        return map.toString();
    }

    public static void main(String[] args) {
        LRUCache<Integer, String> cache = new LRUCache<>(3);
        cache.put(1, "one");
        cache.put(2, "two");
        cache.put(3, "three");
        cache.get(1);              // access 1, making 2 the least recently used
        cache.put(4, "four");      // evicts key 2
        System.out.println(cache); // expected entries: 3, 1, 4 in access order
    }
}
