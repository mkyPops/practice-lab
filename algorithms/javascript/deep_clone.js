/**
 * deepClone.js
 *
 * Deep clone utility that recursively copies plain objects, arrays,
 * Dates, Maps, Sets, and other common structures while correctly
 * handling circular references via a WeakMap cache.
 */

'use strict';

function deepClone(value, seen = new WeakMap()) {
  // Primitives (including null, undefined, functions, symbols) are returned as-is.
  if (value === null || typeof value !== 'object') {
    return value;
  }

  // If we've already cloned this object, return the existing clone
  // to preserve circular references and shared references.
  if (seen.has(value)) {
    return seen.get(value);
  }

  // Handle Date
  if (value instanceof Date) {
    return new Date(value.getTime());
  }

  // Handle RegExp
  if (value instanceof RegExp) {
    return new RegExp(value.source, value.flags);
  }

  // Handle Map
  if (value instanceof Map) {
    const clonedMap = new Map();
    seen.set(value, clonedMap);
    for (const [key, val] of value) {
      clonedMap.set(deepClone(key, seen), deepClone(val, seen));
    }
    return clonedMap;
  }

  // Handle Set
  if (value instanceof Set) {
    const clonedSet = new Set();
    seen.set(value, clonedSet);
    for (const item of value) {
      clonedSet.add(deepClone(item, seen));
    }
    return clonedSet;
  }

  // Handle Array
  if (Array.isArray(value)) {
    const clonedArr = [];
    seen.set(value, clonedArr);
    for (let i = 0; i < value.length; i++) {
      clonedArr[i] = deepClone(value[i], seen);
    }
    return clonedArr;
  }

  // Handle typed arrays and ArrayBuffer-backed objects.
  if (ArrayBuffer.isView(value)) {
    return value.constructor.from(value);
  }

  // Handle plain objects (and objects with custom prototypes).
  const proto = Object.getPrototypeOf(value);
  const clonedObj = Object.create(proto);
  seen.set(value, clonedObj);

  for (const key of Reflect.ownKeys(value)) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (descriptor && 'value' in descriptor) {
      clonedObj[key] = deepClone(value[key], seen);
    } else if (descriptor) {
      // Preserve getters/setters as-is rather than invoking them.
      Object.defineProperty(clonedObj, key, descriptor);
    }
  }

  return clonedObj;
}

module.exports = deepClone;
