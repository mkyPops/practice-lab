/**
 * deepClone.js
 *
 * A generic deep cloning utility.
 * Supports plain objects, arrays, Dates, Maps, Sets, RegExps,
 * and preserves circular references via a WeakMap seen-cache.
 */

function deepClone(value, seen = new WeakMap()) {
  // Primitives (including null, undefined, functions) are returned as-is.
  if (value === null || typeof value !== 'object') {
    return value;
  }

  // Handle circular references: if we've already cloned this object, reuse it.
  if (seen.has(value)) {
    return seen.get(value);
  }

  // Dates: clone by copying the timestamp.
  if (value instanceof Date) {
    return new Date(value.getTime());
  }

  // RegExps: clone source, flags, and lastIndex.
  if (value instanceof RegExp) {
    const clonedRegExp = new RegExp(value.source, value.flags);
    clonedRegExp.lastIndex = value.lastIndex;
    return clonedRegExp;
  }

  // Arrays: create an empty array first so it can be registered
  // in `seen` before recursing (handles circular refs inside arrays).
  if (Array.isArray(value)) {
    const clonedArray = [];
    seen.set(value, clonedArray);
    value.forEach((item, index) => {
      clonedArray[index] = deepClone(item, seen);
    });
    return clonedArray;
  }

  // Maps: clone keys and values recursively.
  if (value instanceof Map) {
    const clonedMap = new Map();
    seen.set(value, clonedMap);
    for (const [key, val] of value.entries()) {
      clonedMap.set(deepClone(key, seen), deepClone(val, seen));
    }
    return clonedMap;
  }

  // Sets: clone each entry recursively.
  if (value instanceof Set) {
    const clonedSet = new Set();
    seen.set(value, clonedSet);
    for (const item of value.values()) {
      clonedSet.add(deepClone(item, seen));
    }
    return clonedSet;
  }

  // Plain objects (and objects with custom prototypes): preserve prototype chain.
  const clonedObject = Object.create(Object.getPrototypeOf(value));
  seen.set(value, clonedObject);
  for (const key of Object.keys(value)) {
    clonedObject[key] = deepClone(value[key], seen);
  }

  return clonedObject;
}

module.exports = deepClone;
