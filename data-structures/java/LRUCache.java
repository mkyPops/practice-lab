/**
 * A generic, thread-unsafe LRU (Least Recently Used) cache implementation
 * backed by a LinkedHashMap in access-order mode. Both get and put run in
 * amortized O(1) time, since LinkedHashMap maintains an internal doubly
 * linked list to track usage order and a hash table for direct lookups.
 * When the cache exceeds its configured capacity, the least recently
 * used entry is automatically evicted.
 */
import java.util.LinkedHashMap;
import java.util.Map;

public class LruCache<K, V> {

    private final int capacity;
    private final LinkedHashMap<K, V> map;

    public LruCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive");
        }
        this.capacity = capacity;
        // accessOrder = true moves entries to the end of the iteration order on get/put
        this.map = new LinkedHashMap<K, V>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                // Evict the eldest (least recently used) entry once capacity is exceeded
                return size() > LruCache.this.capacity;
            }
        };
    }

    /** Returns the value for the given key, or null if absent, updating its recency. */
    public synchronized V get(K key) {
        return map.get(key);
    }

    /** Inserts or updates a key-value pair, evicting the LRU entry if capacity is exceeded. */
    public synchronized void put(K key, V value) {
        map.put(key, value);
    }

    /** Returns true if the cache contains the given key, without affecting recency. */
    public synchronized boolean containsKey(K key) {
        return map.containsKey(key);
    }

    /** Removes the entry for the given key, returning its value, or null if absent. */
    public synchronized V remove(K key) {
        return map.remove(key);
    }

    /** Returns the current number of entries in the cache. */
    public synchronized int size() {
        return map.size();
    }

    public static void main(String[] args) {
        LruCache<Integer, String> cache = new LruCache<>(3);
        cache.put(1, "one");
        cache.put(2, "two");
        cache.put(3, "three");
        cache.get(1);            // access 1, making 2 the least recently used
        cache.put(4, "four");    // evicts key 2
        System.out.println(cache.containsKey(2)); // false
        System.out.println(cache.get(1));          // one
        System.out.println(cache.get(4));          // four
    }
}
