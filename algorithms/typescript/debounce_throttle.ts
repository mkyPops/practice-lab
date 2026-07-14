/**
 * Generic, typed debounce and throttle higher-order function utilities.
 *
 * - debounce: delays invoking `fn` until `wait` ms have elapsed since the
 *   last call. Supports leading/trailing edge invocation.
 * - throttle: invokes `fn` at most once per `wait` ms window. Supports
 *   leading/trailing edge invocation.
 *
 * Both return a wrapped function with `cancel()` and `flush()` helpers.
 */

type AnyFn = (...args: any[]) => any;

interface DebounceOptions {
  leading?: boolean;
  trailing?: boolean;
}

interface ThrottleOptions {
  leading?: boolean;
  trailing?: boolean;
}

export interface Debounced<F extends AnyFn> {
  (...args: Parameters<F>): void;
  cancel(): void;
  flush(): void;
}

export interface Throttled<F extends AnyFn> {
  (...args: Parameters<F>): void;
  cancel(): void;
  flush(): void;
}

export function debounce<F extends AnyFn>(
  fn: F,
  wait: number,
  options: DebounceOptions = {}
): Debounced<F> {
  const { leading = false, trailing = true } = options;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let lastArgs: Parameters<F> | undefined;
  let lastThis: unknown;
  let invokedOnLeading = false;

  const invoke = () => {
    if (lastArgs) {
      fn.apply(lastThis, lastArgs);
      lastArgs = undefined;
      lastThis = undefined;
    }
  };

  const debounced = function (this: unknown, ...args: Parameters<F>) {
    lastArgs = args;
    lastThis = this;

    const isFirstCall = timer === undefined;
    if (timer !== undefined) clearTimeout(timer);

    if (leading && isFirstCall) {
      invoke();
      invokedOnLeading = true;
    } else {
      invokedOnLeading = false;
    }

    timer = setTimeout(() => {
      timer = undefined;
      // avoid double-invoking on trailing edge if leading already fired this burst
      if (trailing && !invokedOnLeading) invoke();
      lastArgs = undefined;
      lastThis = undefined;
    }, wait);
  } as Debounced<F>;

  debounced.cancel = () => {
    if (timer !== undefined) clearTimeout(timer);
    timer = undefined;
    lastArgs = undefined;
    lastThis = undefined;
  };

  debounced.flush = () => {
    if (timer !== undefined) {
      clearTimeout(timer);
      timer = undefined;
      invoke();
    }
  };

  return debounced;
}

export function throttle<F extends AnyFn>(
  fn: F,
  wait: number,
  options: ThrottleOptions = {}
): Throttled<F> {
  const { leading = true, trailing = true } = options;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let lastCallTime = 0;
  let lastArgs: Parameters<F> | undefined;
  let lastThis: unknown;

  const invoke = () => {
    lastCallTime = Date.now();
    if (lastArgs) {
      fn.apply(lastThis, lastArgs);
      lastArgs = undefined;
      lastThis = undefined;
    }
  };

  const throttled = function (this: unknown, ...args: Parameters<F>) {
    const now = Date.now();
    if (lastCallTime === 0 && !leading) lastCallTime = now;

    const remaining = wait - (now - lastCallTime);
    lastArgs = args;
    lastThis = this;

    if (remaining <= 0 || remaining > wait) {
      if (timer !== undefined) {
        clearTimeout(timer);
        timer = undefined;
      }
      invoke();
    } else if (trailing && timer === undefined) {
      timer = setTimeout(() => {
        timer = undefined;
        invoke();
      }, remaining);
    }
  } as Throttled<F>;

  throttled.cancel = () => {
