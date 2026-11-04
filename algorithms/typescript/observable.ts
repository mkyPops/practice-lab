/**
 * A minimal Observable implementation supporting subscribe, map, filter,
 * and unsubscribe. Values are pushed synchronously to subscribers.
 */

type Observer<T> = (value: T) => void;
type Unsubscribe = () => void;
type Producer<T> = (observer: Observer<T>) => Unsubscribe | void;

class Observable<T> {
  private readonly producer: Producer<T>;

  constructor(producer: Producer<T>) {
    this.producer = producer;
  }

  // Registers an observer and returns an unsubscribe function.
  subscribe(observer: Observer<T>): Unsubscribe {
    const cleanup = this.producer(observer);
    return () => {
      if (typeof cleanup === 'function') {
        cleanup();
      }
    };
  }

  // Creates a new Observable that transforms emitted values.
  map<U>(fn: (value: T) => U): Observable<U> {
    return new Observable<U>((observer) => {
      return this.subscribe((value) => observer(fn(value)));
    });
  }

  // Creates a new Observable that only emits values passing the predicate.
  filter(predicate: (value: T) => boolean): Observable<T> {
    return new Observable<T>((observer) => {
      return this.subscribe((value) => {
        if (predicate(value)) {
          observer(value);
        }
      });
    });
  }

  // Convenience factory for emitting a fixed set of values synchronously.
  static of<T>(...values: T[]): Observable<T> {
    return new Observable<T>((observer) => {
      for (const value of values) {
        observer(value);
      }
    });
  }
}

// --- Example usage ---

const numbers$ = Observable.of(1, 2, 3, 4, 5, 6);

const unsubscribe = numbers$
  .filter((n) => n % 2 === 0)
  .map((n) => n * 10)
  .subscribe((value) => console.log('Received:', value));

unsubscribe();

export { Observable };
