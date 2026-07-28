/**
 * memoize.js
 *
 * A generic memoization utility. Wraps any pure function so that results
 * are cached based on the signature (arguments) of each call. Supports
 * a custom key resolver, an optional maximum cache size (simple LRU
 * eviction), and exposes cache management helpers on the returned function.
 */

function defaultResolver(...args) {
  // Serialize arguments into a stable cache key. Falls back to String()
  // for values that can't be JSON-stringified (e.g. functions, symbols).
  return args
    .map((arg) => {
      try {
        return JSON.stringify(arg);
      } catch {
        return String(arg);
      }
    })
    .join('|');
}

function memoize(fn, { resolver = defaultResolver, maxSize = Infinity } = {}) {
  if (typeof fn !== 'function') {
    throw new TypeError('memoize expects a function as its first argument');
  }

  const cache = new Map();

  function memoized(...args) {
    const key = resolver(...args);

    if (cache.has(key)) {
      // Refresh recency for basic LRU behavior.
      const value = cache.get(key);
      cache.delete(key);
      cache.set(key, value);
      return value;
    }

    const result = fn.apply(this, args);
    cache.set(key, result);

    // Evict the least recently used entry once over capacity.
    if (cache.size > maxSize) {
      const oldestKey = cache.keys().next().value;
      cache.delete(oldestKey);
    }

    return result;
  }

  memoized.cache = cache;
  memoized.clear = () => cache.clear();
  memoized.delete = (...args) => cache.delete(resolver(...args));

  return memoized;
}

module.exports = memoize;
