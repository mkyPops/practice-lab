/**
 * A generic, strongly-typed event emitter.
 *
 * Consumers define an event map interface where each key is an event name
 * and each value is the tuple of argument types for that event's payload.
 * All `on`/`off`/`once`/`emit` calls are then checked against that map.
 *
 * Example:
 *   interface Events {
 *     greet: [name: string];
 *     tick: [count: number];
 *   }
 *   const emitter = new TypedEventEmitter<Events>();
 *   emitter.on('greet', (name) => console.log(`Hello, ${name}`));
 *   emitter.emit('greet', 'World');
 */

type EventMap = Record<string, unknown[]>;

type Listener<Args extends unknown[]> = (...args: Args) => void;

export class TypedEventEmitter<Events extends EventMap> {
  private listeners: {
    [K in keyof Events]?: Set<Listener<Events[K]>>;
  } = {};

  /** Register a listener for an event. */
  on<K extends keyof Events>(event: K, listener: Listener<Events[K]>): this {
    const set = this.listeners[event] ?? new Set();
    set.add(listener);
    this.listeners[event] = set;
    return this;
  }

  /** Remove a previously registered listener. */
  off<K extends keyof Events>(event: K, listener: Listener<Events[K]>): this {
    this.listeners[event]?.delete(listener);
    return this;
  }

  /** Register a listener that fires only once, then auto-removes itself. */
  once<K extends keyof Events>(event: K, listener: Listener<Events[K]>): this {
    const wrapper: Listener<Events[K]> = (...args) => {
      this.off(event, wrapper);
      listener(...args);
    };
    return this.on(event, wrapper);
  }

  /** Synchronously invoke all listeners registered for an event. */
  emit<K extends keyof Events>(event: K, ...args: Events[K]): boolean {
    const set = this.listeners[event];
    if (!set || set.size === 0) return false;
    // Copy to array so listeners added/removed during emit don't affect this pass.
    for (const listener of Array.from(set)) {
      listener(...args);
    }
    return true;
  }

  /** Remove all listeners for a specific event, or all events if omitted. */
  removeAllListeners<K extends keyof Events>(event?: K): this {
    if (event === undefined) {
      this.listeners = {};
    } else {
      delete this.listeners[event];
    }
    return this;
  }
}
