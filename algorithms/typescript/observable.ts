/**
 * A minimal Observable implementation supporting subscribe, map, filter,
 * and unsubscribe. Not spec-compliant with TC39 Observable, just a small
 * educational/utility version for synchronous or async push-based streams.
 */

type Observer<T> = (value: T) => void;
type Subscription = { unsubscribe: () => void };
type Producer<T> = (observer: Observer<T>) => (() => void) | void;

class Observable<T> {
  constructor(private readonly producer: Producer<T>) {}

  subscribe(observer: Observer<T>): Subscription {
    let unsubscribed = false;

    // Wrap the observer so we stop delivering values after unsubscribe.
    const guardedObserver: Observer<T> = (value) => {
      if (!unsubscribed) observer(value);
    };

    const cleanup = this.producer(guardedObserver);

    return {
      unsubscribe: () => {
        if (unsubscribed) return;
        unsubscribed = true;
        if (typeof cleanup === "function") cleanup();
      },
    };
  }

  map<U>(fn: (value: T) => U): Observable<U> {
    return new Observable<U>((observer) => {
      const sub = this.subscribe((value) => observer(fn(value)));
      return () => sub.unsubscribe();
    });
  }

  filter(predicate: (value: T) => boolean): Observable<T> {
    return new Observable<T>((observer) => {
      const sub = this.subscribe((value) => {
        if (predicate(value)) observer(value);
      });
      return () => sub.unsubscribe();
    });
  }

  static of<T>(...values: T[]): Observable<T> {
    return new Observable<T>((observer) => {
      for (const value of values) observer(value);
    });
  }
}

// --- Example usage ---
const numbers = Observable.of(1, 2, 3, 4, 5, 6);

const subscription = numbers
  .filter((n) => n % 2 === 0)
  .map((n) => n * 10)
  .subscribe((value) => console.log("Received:", value));

subscription.unsubscribe();

export { Observable, Observer, Subscription };
