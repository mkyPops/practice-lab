/**
 * A generic, strongly-typed EventEmitter.
 *
 * Consumers define an event map interface where each key is an event name
 * and each value is the tuple of argument types emitted for that event.
 * This gives full type-safety and autocompletion for `on`, `off`, `once`,
 * and `emit` calls.
 *
 * Example:
 *   interface Events {
 *     greet: [name: string];
 *     error: [err: Error];
 *   }
 *   const emitter = new TypedEventEmitter<Events>();
 *   emitter.on('greet', (name) => console.log(`Hello, ${name}`));
 *   emitter.emit('greet', 'World');
 */

type EventMap = Record<string, unknown[]>;

type Listener<Args extends unknown[]> = (...args: Args) => void;

export class TypedEventEmitter<TEvents extends EventMap> {
  private listeners: {
    [K in keyof TEvents]?: Set<Listener<TEvents[K]>>;
  } = {};

  /** Register a listener for an event. */
  on<K extends keyof TEvents>(event: K, listener: Listener<TEvents[K]>): this {
    const set = this.listeners[event] ?? new Set();
    set.add(listener);
    this.listeners[event] = set;
    return this;
  }

  /** Remove a previously registered listener for an event. */
  off<K extends keyof TEvents>(event: K, listener: Listener<TEvents[K]>): this {
    this.listeners[event]?.delete(listener);
    return this;
  }

  /** Register a listener that is invoked at most once, then auto-removed. */
  once<K extends keyof TEvents>(event: K, listener: Listener<TEvents[K]>): this {
    const wrapper: Listener<TEvents[K]> = (...args) => {
      this.off(event, wrapper);
      listener(...args);
    };
    return this.on(event, wrapper);
  }

  /** Synchronously invoke all listeners registered for an event. */
  emit<K extends keyof TEvents>(event: K, ...args: TEvents[K]): boolean {
    const set = this.listeners[event];
    if (!set || set.size === 0) return false;
    // Copy to array so listeners added/removed during emit don't affect this pass.
    for (const listener of Array.from(set)) {
      listener(...args);
    }
    return true;
  }

  /** Remove all listeners for a specific event, or all events if omitted. */
  removeAllListeners<K extends keyof TEvents>(event?: K): this {
    if (event === undefined) {
      this.listeners = {};
    } else {
      delete this.listeners[event];
    }
    return this;
  }
}
